# GeminiCLI Agent Team Action Plan

このドキュメントでは、複数の専門エージェントが連携してタスクを解決する「Agent Team」アーキテクチャに基づいた開発プランを定義します。
リーダーによる統率、アーキテクトによる設計、コーダーによる実装・相談という、**企業の開発チームのような役割分担**を実現します。

## 1. プロジェクトの概要 (The Collaborative Squad)

### チーム構成と役割 (The Roster)

1.  **Manager (Leader/PM)**
    *   **役割**: プロジェクト全体の進行管理、タスクの分解と割り当て、各メンバーの相談窓口。
    *   **責任**: ユーザー要望のヒアリング -> Architectへ設計指示 -> 設計に基づく実装タスクのCoderへの配分 -> 進捗確認。
2.  **Architect (Technical Lead)**
    *   **役割**: **技術選定、ディレクトリ構造の設計、要件定義書の作成**。
    *   **責任**: 
        - ユーザーの要望を実現するための最適な技術スタック（言語、ライブラリ）を選定。
        - プロジェクトのファイル構成（ディレクトリツリー）を定義。
        - 実装の詳細な仕様書（Spec）を作成し、Managerに渡す。
3.  **Coders (Developers)**
    *   **役割**: 設計書に基づいた実装。
    *   **行動**: 
        - 割り当てられた機能を実装。
        - **Manager/Architectに仕様の不明点を相談**する。
        - 進捗を報告し、完了したコードを提出。
4.  **Reviewer (QA)**
    *   **役割**: コードレビューと品質保証。

## 2. 開発フェーズ

### フェーズ 0: 環境構築 (Environment Setup)
- [x] **Docker環境**:
    - `Dockerfile`: Python 3.12 + uv (multistage build)。
    - `compose.yaml`: ボリュームマウント（ソースコード）、環境変数の設定。
- [x] **パッケージ管理 (uv)**:
    - `pyproject.toml` の作成と依存関係の定義。
    - `uv.lock` の生成。

### フェーズ 1: エージェント基盤と通信 (Foundation)
- [x] **Agent Base Class**: 全エージェントの基底クラス（メッセージング、履歴管理、API通信）。
- [x] **Manager Agent (Initial)**: リーダーエージェントの基本クラスとタスク分解のスタブ実装。
- [x] **CLIチャットインターフェース**: `main.py` による対話型CLI。

### フェーズ 2: 設計のエキスパート "Architect" (Design Phase)
- [ ] **Architect Agent 実装**: 専門設計エージェントのクラス作成。
- [ ] **要件定義スキル**: ユーザーの曖昧な指示から「何を」「どう」作るかを定義するプロンプト。
- [ ] **構造設計スキル**: 
    - `propose_structure(tree)`: ディレクトリ構成を提案するツール。
    - `define_tech_stack(stack)`: 使用技術を決定するツール。
- [ ] **Managerとの連携**: 設計書（Markdown等）を成果物としてManagerに渡すフロー。

### フェーズ 3: マネージャーの「管理・采配」 (Management Phase)
- [ ] **タスク分解の実装**: Architectの設計書をLLMで解析し、実装タスクに分割する。
- [ ] **アサイン機能**: サブエージェントを動的に生成・割り振る仕組み。
- [ ] **相談ハブ機能**: Coderからの質問に対し、Architectの設計意図を確認しつつ回答を返す仲介機能。

### フェーズ 4: コーダーの実装と報連相 (Implementation Phase)
- [ ] **Coder Agent 実装**: 実装に特化したエージェント。
- [ ] **実装と相談**: 
    - `ask_question(to_whom, content)`: 誰（Manager/Architect）に何を聞くか。
    - 実装 -> 疑問 -> 質問 -> 回答 -> 実装再開 のループ。

### フェーズ 5: 統合テストとワークフロー (Integration)
- [ ] **開発フロー**:
    1.  **User**: 「TODOアプリ作りたい」
    2.  **Manager** -> **Architect**: 「技術選定と設計お願い」
    3.  **Architect**: 「FastAPI + React + SQLiteで、構成はこうです」 (設計書提出)
    4.  **Manager**: 「了解。ではCoder AはAPI、Coder BはReact担当で」 (タスク割り当て)
    5.  **Coders**: 実装開始。不明点はManager経由でArchitectに確認も可能。

## 3. 技術スタック
- **言語**: Python 3.12+
- **LLM**: Gemini 2.0 Flash / Pro (gemini-flash-lite-latest 活用)
- **Environment**: Docker (Containerized) + uv (Package Manager)
- **Architecture**: Multi-Agent System (MAS)
- **CLI**: Typer + Rich
- **Testing**: pytest
- **Documentation**: doc/ADR, doc/post-mortems, doc/dev-log (Template-based)

## 4. 実行手順案（開発フロー）

1. **起動**: `docker compose exec agent-team python src/main.py`
2. **要件定義**: User -> Manager -> **Architect** (設計書作成)
3. **計画**: Manager (タスク分解)
4. **実装**: Manager -> **Coders** (並列開発 & 報連相)
5. **完了**: Reviewer -> Manager -> User
