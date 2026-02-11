# GeminiCLI Agent Team: Collaborative AI Development

このプロジェクトは、**複数の専門AIエージェント（Manager, Architect, Coder, Reviewer）がチームを組み、対話と協調によってユーザーの課題を解決する自律型開発環境**「GeminiCLI Agent Team」です。

## コンセプト: The Professional Squad

本システムの核は、**リーダー（Manager）による統率、アーキテクト（Architect）による設計、コーダー（Coder）による実装・報連相のループ**です。

### 1. Manager (The Leader & PM)
- **統括 (Orchestrator)**:
  ユーザーの要望をヒアリングし、プロジェクト全体を管理する。
- **タスク割り当て (Task Assignment)**:
  Architectが作成した設計に基づき、具体的な実装タスクをCoderに振り分ける。
- **相談窓口 (Consultation Hub)**:
  メンバーからの質問に答え、全体の意思統一を図る。

### 2. Architect (The Designer)
- **技術選定 (Technology Stack)**:
  ユーザーの要件に対して最適な技術（言語、フレームワーク、DB等）を選定する。
- **設計 (System Structure)**:
  ディレクトリ構造、ファイル構成、データモデリングなどの要件定義書を作成し、Managerに提出する。
- **技術的相談役 (Tech Advisor)**:
  Coderからの技術的な質問に対し、設計意図を説明する。

### 3. Coder (The Implementer)
- **実装 (Implementation)**:
  割り当てられたタスク（機能実装、バグ修正）を実行する。
- **報連相 (Report & Consult)**:
  - **相談**: 実装中に不明点があれば、ManagerやArchitectに質問する。
  - **報告**: 進捗状況や成果物をManagerに報告する。

### 4. Reviewer (Quality Assurance)
- **品質チェック (Review)**:
  提出されたコードのレビュー、セキュリティチェック、統合テストを行う。

## ワークフロー例

1.  **ユーザー**: 「タスク管理のWebアプリを作りたい」
2.  **Manager**: 「了解。**Architect**、技術選定と設計をお願い。」
3.  **Architect**: 「Python (Django) + Reactにします。ディレクトリ構成はこうです...」 (設計書提出)
4.  **Manager**: 「ありがとう。では**Coder A**はDjangoのモデルとAPIを、**Coder B**はReactのUIをお願い。」
5.  **Coder A**: （実装中）「認証はJWTでいいですか？」 -> **Manager** (必要ならArchitectに確認) 「はい、JWTで。」
6.  **Coders**: 実装完了 -> 報告。
7.  **Manager**: 全体完了を確認 -> ユーザーへ納品。

## アクションプラン

詳細な実装手順は [ACTION_PLAN.md](./ACTION_PLAN.md) を参照してください。

## 実行要件

- **Docker**: 必須 (開発・実行環境)
- **uv**: 推奨 (ローカルでのパッケージ管理も行う場合)
- **API Key**: Gemini API Key (Google AI Studio)

## 開始方法 (Docker + uv)

1. リポジトリのクローンとディレクトリ移動
   ```bash
   git clone <your-repo-url>
   cd gemini-cli-agent-team
   ```



2. 環境変数の設定
   `.env` ファイルを作成し、APIキーを設定します。
   ```bash
   echo "GEMINI_API_KEY=your_api_key_here" > .env
   # モデル名を指定する場合 (Optional, default: gemini-2.5-flash-lite)
   # echo "GEMINI_MODEL_NAME=gemini-2.5-flash" >> .env
   ```

3. コンテナのビルドと起動 (バックグラウンド実行)
   ```bash
   docker compose up -d --build
   ```
   > **Note**: `.env` ファイルを変更した場合（例: モデル名の変更）は、`docker compose up -d` を再実行することで変更が反映されます（`--build` オプションは不要です）。依存パッケージを追加した場合は `--build` が必要です。

4. エージェントチームとの対話 (CLIの起動)
   コンテナ内でアプリケーションを実行します。
   ```bash
   docker compose exec agent-team python src/main.py
   ```
   
   起動すると、Managerエージェントとのチャットセッションが開始されます。
   終了するには `exit` または `quit` と入力してください。

5. テストの実行 (単体テスト)
   `pytest` を使用してテストを実行します。
   ```bash
   docker compose exec agent-team pytest src/tests
   ```

## 開発ガイド (Development Guide)

- **依存関係の追加**:
  新しいライブラリを追加する場合は、`pyproject.toml` を編集するか、コンテナ内で以下を実行してください。
  ```bash
  # 例: pandasを追加する場合
  docker compose exec agent-team uv add pandas
  # または pyproject.toml 編集後に同期
  docker compose exec agent-team uv sync
  ```
- **ソースコード**: `./src` ディレクトリに配置。
- **成果物**: エージェントが生成するファイルは `./sandbox` に配置されます。
