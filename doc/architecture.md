# GeminiCLI Agent Team - アーキテクチャ設計

本ドキュメントでは、自律的エージェントチームの中核となる `Agent` クラスの設計と、エージェント間のインタラクションを記述します。

## 1. クラス図 (Class Diagram)

基底クラス `Agent` を定義し、具体的な役割を持つエージェントがそれを継承します。

```mermaid
classDiagram
    class Agent {
        <<abstract>>
        +str name
        +str role
        +list history
        +object model
        +list tools
        +__init__(name, role, model_config)
        +receive_message(message: str, sender: str)
        +think() Response
        +execute_tool(tool_name, args) Result
        +send_message(recipient: Agent, message: str)
    }

    class ManagerAgent {
        +assign_task(task: str, worker: Agent)
        +review_progress()
    }

    class ArchitectAgent {
        +design_structure(requirements: str)
        +select_technology()
    }

    class CoderAgent {
        +write_code(spec: str)
        +debug_code(error: str)
    }

    class ReviewerAgent {
        +review_code(code: str)
        +run_tests()
    }

    Agent <|-- ManagerAgent
    Agent <|-- ArchitectAgent
    Agent <|-- CoderAgent
    Agent <|-- ReviewerAgent
```

## 2. シーケンス図 (Sequence Diagram) - 思考とツール実行ループ

エージェントがメッセージを受け取り、思考（LLM推論）し、必要に応じてツールを実行して、最終的な回答を返すまでのフローです。

```mermaid
sequenceDiagram
    participant User
    participant Agent
    participant LLM
    participant Tool

    User->>Agent: メッセージ送信 ("これを作って")
    Agent->>Agent: 履歴に追加 (add_to_history)

    loop ReAct Loop (思考と行動)
        Agent->>LLM: プロンプト送信 (履歴 + 現在の状態)
        LLM-->>Agent: 応答 (思考 Or ツール呼び出し要求)

        alt ツール呼び出し要求の場合
            Agent->>Tool: ツール実行 (args)
            Tool-->>Agent: 実行結果 (Result)
            Agent->>LLM: 結果をフィードバック (Observation)
        else 最終回答の場合
            Agent->>Agent: ループ終了
        end
    end

    Agent-->>User: 最終回答 ("できました")
```

## 3. エージェント間通信 (Interaction) - タスク委譲の詳細

Managerがユーザーの依頼を解釈し、Architectに設計を、Coderに実装を段階的に委譲して成果を得るフローです。

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant CLI as main.py
    participant M as Manager (Agent)
    participant A as Architect (Agent)
    participant C as Coder (Agent)
    participant S as Sandbox (Filesystem/Subprocess)
    participant LLM as Gemini API

    User->>CLI: 指示入力 (例: "新しいアプリを作って")
    CLI->>M: send_message
    
    Note over M, LLM: Manager思考
    M->>LLM: _call_api
    LLM-->>M: tool_call: delegate_task(to="Architect", ...)
    
    rect rgb(240, 240, 255)
        Note over M, A: 【設計フェーズ】
        M->>A: send_message(設計依頼)
        A->>LLM: _call_api
        LLM-->>A: 設計案 (Markdown/構造案)
        A-->>M: 設計ドキュメント
    end

    Note over M, LLM: Manager思考 (設計受領後)
    M->>LLM: _call_api
    LLM-->>M: tool_call: delegate_task(to="Coder", ...)

    rect rgb(240, 240, 240)
        Note over M, C: 【実装フェーズ】
        M->>C: send_message(実装依頼 + 設計案)
        
        rect rgb(220, 240, 220)
            Note over C, LLM: Coder内部ループ
            C->>LLM: _call_api
            LLM-->>C: tool_call: write_to_sandbox
            C->>S: Write File
            LLM-->>C: tool_call: execute_in_sandbox
            C->>S: Run & Verify
            S-->>C: Result
            LLM-->>C: "Complete"
        end
        
        C-->>M: 実装完了報告
    end

    M->>LLM: tool_result (Delegate Result)
    LLM-->>M: 最終回答
    M-->>CLI: Response Text
    CLI->>User: 完了報告
```
