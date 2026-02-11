import os
from pathlib import Path
from typing import Dict, Any
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
        4. 不明な点がある場合は、Manager に対して質問を行う。
        """
        instructions = """
        実装を行う際は、まず指示された要件を正しく理解しているか確認し、その後実装に入ってください。
        コードを生成したら、必ず `write_to_sandbox` を使用して物理ファイルとして保存してください。
        保存先のパスは `sandbox/` ディレクトリ起点の相対パスで指定してください。
        """
        super().__init__(name, role, instructions, tools=[self.write_to_sandbox])
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

    def execute_tool(self, tool_name: str, args: Dict[str, Any]) -> Any:
        if tool_name == "write_to_sandbox":
            return self.write_to_sandbox(**args)
        return f"Tool {tool_name} not found."
