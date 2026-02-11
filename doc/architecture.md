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

## 3. エージェント間通信 (Interaction) - タスク委譲

ManagerがタスクをCoderに委譲し、結果を受け取るフロー。

```mermaid
sequenceDiagram
    participant User
    participant Manager
    participant Coder

    User->>Manager: "ログイン機能を作って"
    Manager->>Manager: タスク分解 & 計画
    
    Manager->>Coder: "JWT認証の実装をお願い" (Delegate)
    Coder->>Coder: 実装作業 (Think & Tool Loop)
    Coder-->>Manager: "実装完了。ファイルは src/auth.py です" (Report)

    Manager->>Manager: 成果物確認
    Manager-->>User: "ログイン機能の実装が完了しました"
```
