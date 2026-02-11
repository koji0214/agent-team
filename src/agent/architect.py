from typing import Dict, Any, List
import os
from pathlib import Path
from rich.console import Console
try:
    from .agent import Agent
except ImportError:
    from agent.agent import Agent

console = Console()

class Architect(Agent):
    """
    システムの設計（ディレクトリ構造、技術選定、仕様定義）を担当するエージェント。
    """
    
    def __init__(self, name: str = "Architect"):
        # プロジェクトルートからの相対パスで設計書の保存場所を特定
        # 主に docs/architecture/ 配下を使用することを想定
        self.project_root = Path(".").resolve()
        
        role = """
        あなたはプロジェクトのアーキテクト（Technical Lead）です。
        以下の責任を持ちます：
        1. ユーザーの要望を実現するための最適な技術スタックを選定する。
        2. プロジェクトのディレクトリ構造を定義する。
        3. 実装の詳細な仕様書（Markdown形式）を作成し `write_design_doc` ツールで保存する。
        4. 既存のファイル構成を `list_project_files` ツールで確認し、整合性の取れた設計を行う。
        
        回答は常に論理的かつ構造的である必要があります。
        """
        instructions = """
        設計を行う際は、まず全体像を把握し、拡張性と保守性を考慮した構成案を提示してください。
        必要に応じてディレクトリツリーをMarkdownのコードブロックで表現してください。
        設計書を作成したら、必ずファイルに保存して成果物として残してください。
        """
        super().__init__(name, role, instructions)
        # ツールを登録
        self.tools = [self.write_design_doc, self.list_project_files]

    def write_design_doc(self, file_path: str, content: str) -> str:
        """
        設計書（Markdown等）を指定されたパスに保存します。
        
        Args:
            file_path (str): 保存先の相対パス（例: 'docs/architecture/system_design.md'）。
            content (str): ファイルの内容。
            
        Returns:
            str: 保存結果のメッセージ。
        """
        try:
            # パスの解決とセキュリティチェック
            target_path = (self.project_root / file_path).resolve()
            
            # プロジェクトルート外への書き込み禁止
            if not str(target_path).startswith(str(self.project_root)):
                return f"Error: Security violation. Cannot write outside project root."

            # ディレクトリの作成
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # ファイルの書き込み
            with open(target_path, "w", encoding="utf-8") as f:
                f.write(content)
                
            console.print(f"[bold green]Architect saved design doc:[/bold green] {file_path}")
            return f"Successfully saved design document to {file_path}."
            
        except Exception as e:
            error_msg = f"Error saving file: {str(e)}"
            console.print(f"[bold red]{error_msg}[/bold red]")
            return error_msg

    def list_project_files(self, directory: str = ".", max_depth: int = 2) -> str:
        """
        指定されたディレクトリ以下のファイル構造を確認します。
        
        Args:
            directory (str): 確認したいディレクトリ（デフォルトはルート）。
            max_depth (int): 探索する深さ。
            
        Returns:
            str: ディレクトリツリーのテキスト表現。
        """
        try:
            root_path = (self.project_root / directory).resolve()
            
            # ルート外へのアクセス禁止
            if not str(root_path).startswith(str(self.project_root)):
                return f"Error: Security violation. Cannot access outside project root."
            
            if not root_path.exists():
                return f"Error: Directory '{directory}' does not exist."

            tree_str = f"Directory structure of '{directory}':\n"
            
            for root, dirs, files in os.walk(root_path):
                # 深さ制限の計算
                depth = str(Path(root).relative_to(root_path)).count(os.sep)
                if depth >= max_depth:
                    continue
                
                # インデント
                indent = "  " * depth
                subindent = "  " * (depth + 1)
                
                relative_root = Path(root).relative_to(root_path)
                if str(relative_root) != ".":
                    tree_str += f"{indent}- {relative_root.name}/\n"
                
                for f in files:
                    if not f.startswith("."): # ドットファイルを除外
                        tree_str += f"{subindent}- {f}\n"
                        
            return tree_str
            
        except Exception as e:
            return f"Error listing files: {str(e)}"

    def execute_tool(self, tool_name: str, args: Dict[str, Any]) -> Any:
        if tool_name == "write_design_doc":
            return self.write_design_doc(**args)
        elif tool_name == "list_project_files":
            return self.list_project_files(**args)
        return f"Tool {tool_name} not found."
