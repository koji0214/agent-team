import os
import subprocess
from pathlib import Path
from typing import Dict, Any, List
from rich.console import Console

# 相対インポートを使用（srcパッケージ内での実行を想定）
try:
    from .agent import Agent
except ImportError:
    # テスト時などのために絶対インポートへのフォールバック
    from agent.agent import Agent

console = Console()

class Coder(Agent):
    """
    設計書や指示に基づき、具体的なソースコードを実装するエージェント。
    """
    
    def __init__(self, name: str = "Coder"):
        role = """
        あなたは熟練のソフトウェアエンジニア（Coder）です。
        以下の責任を持ちます：
        1. Manager または Architect から提供された設計書・指示に基づき、高品質なコードを記述する。
        2. プログラミング言語のベストプラクティスに従い、読みやすく保守性の高いコードを書く。
        3. 実装したコードを `write_to_sandbox` ツールを使ってファイルとして保存する。
        4. 保存したコードを `execute_in_sandbox` ツールを使って実行し、期待通りに動作するか検証する。
        5. エラーが発生した場合は、出力を確認して修正を行う。
        6. 実装中に不明な点や仕様の確認が必要な場合は、`ask_question` ツールを使って Manager や Architect に質問を行う。
        """
        instructions = """
        実装を行う際は、まず指示された要件を正しく理解しているか確認し、その後実装に入ってください。
        コードを生成したら、必ず `write_to_sandbox` を使用して物理ファイルとして保存してください。
        保存後は `execute_in_sandbox` を使用して動作確認を行い、正常に動作することを確認してから完了報告をしてください。
        分からないことや相談したいことがあれば、躊躇せずに `ask_question` を使用して質問してください。
        質問した後は、その回答を待つために一度思考をまとめ、Managerに現在の状況を報告してください。
        """
        super().__init__(name, role, instructions, tools=[self.write_to_sandbox, self.execute_in_sandbox, self.ask_question])
        # プロジェクトルートからの相対パスでsandboxの場所を特定
        self.sandbox_dir = Path("sandbox")
        if not self.sandbox_dir.exists():
            self.sandbox_dir.mkdir(parents=True, exist_ok=True)

    def write_to_sandbox(self, file_path: str, content: str) -> str:
        """
        生成したコードやファイルを、安全な sandbox ディレクトリ内に保存します。
        
        Args:
            file_path (str): 保存するファイルの相対パス（例: 'app.py', 'utils/helper.py'）。
            content (str): ファイルの内容（ソースコードなど）。
            
        Returns:
            str: 保存結果のメッセージ。
        """
        try:
            # 安全のためパスを正規化し、境界外へのアクセスを防止
            target_path = (self.sandbox_dir / file_path).resolve()
            
            # sandbox_dir の外に出ようとしていないかチェック
            if not str(target_path).startswith(str(self.sandbox_dir.resolve())):
                return f"Error: Security violation. Cannot write outside sandbox directory."

            # 親ディレクトリが存在しない場合は作成
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # ファイルの書き込み
            with open(target_path, "w", encoding="utf-8") as f:
                f.write(content)
                
            console.print(f"[bold green]Coder saved file:[/bold green] {file_path}")
            return f"Successfully saved {file_path} to sandbox."
            
        except Exception as e:
            error_msg = f"Error saving file: {str(e)}"
            console.print(f"[bold red]{error_msg}[/bold red]")
            return error_msg

    def execute_in_sandbox(self, command: str) -> str:
        """
        sandbox ディレクトリ内でシェルコマンドを実行し、その結果を返します。
        
        Args:
            command (str): 実行するコマンド（例: 'python app.py'）。
            
        Returns:
            str: 標準出力と標準エラーの内容。
        """
        try:
            console.print(f"[bold cyan]Coder executing in sandbox:[/bold cyan] {command}")
            
            # sandboxディレクトリ内でコマンドを実行
            result = subprocess.run(
                command,
                shell=True,
                cwd=self.sandbox_dir,
                capture_output=True,
                text=True,
                timeout=30  # 暴走防止のためタイムアウトを設定
            )
            
            output = f"Exit Code: {result.returncode}\n"
            if result.stdout:
                output += f"STDOUT:\n{result.stdout}\n"
            if result.stderr:
                output += f"STDERR:\n{result.stderr}\n"
            
            return output
            
        except subprocess.TimeoutExpired:
            return "Error: Command timed out after 30 seconds."
        except Exception as e:
            return f"Error executing command: {str(e)}"

    def ask_question(self, to_whom: str, question: str) -> str:
        """
        Manager または Architect に対し、仕様の不明点や技術的な相談を行います。
        
        Args:
            to_whom (str): 質問相手（"Manager" または "Architect"）。
            question (str): 質問の具体的な内容。
            
        Returns:
            str: 質問を送信したことを示すメッセージ。
        """
        console.print(f"[bold yellow]Coder asking {to_whom}:[/bold yellow] {question}")
        return f"質問を {to_whom} に送信しました。回答を得るために、現在のメッセージを終了して Manager の指示を待ってください。"

    def execute_tool(self, tool_name: str, args: Dict[str, Any]) -> Any:
        if tool_name == "write_to_sandbox":
            return self.write_to_sandbox(**args)
        elif tool_name == "execute_in_sandbox":
            return self.execute_in_sandbox(**args)
        elif tool_name == "ask_question":
            return self.ask_question(**args)
        return f"Tool {tool_name} not found."
