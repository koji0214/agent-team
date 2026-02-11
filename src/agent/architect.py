from typing import Dict, Any, List
try:
    from .agent import Agent
except ImportError:
    from agent.agent import Agent

class Architect(Agent):
    """
    システムの設計（ディレクトリ構造、技術選定、仕様定義）を担当するエージェント。
    """
    
    def __init__(self, name: str = "Architect"):
        role = """
        あなたはプロジェクトのアーキテクト（Technical Lead）です。
        以下の責任を持ちます：
        1. ユーザーの要望を実現するための最適な技術スタックを選定する。
        2. プロジェクトのディレクトリ構造を定義する。
        3. 実装の詳細な仕様書（Markdown形式）を作成し、Managerに提出する。
        
        回答は常に論理的かつ構造的である必要があります。
        """
        instructions = """
        設計を行う際は、まず全体像を把握し、拡張性と保守性を考慮した構成案を提示してください。
        必要に応じてディレクトリツリーをMarkdownのコードブロックで表現してください。
        """
        super().__init__(name, role, instructions)

    def execute_tool(self, tool_name: str, args: Dict[str, Any]) -> Any:
        # TODO: 今後、ファイルの書き出しなどのツールを追加予定
        pass
