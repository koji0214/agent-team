from typing import Dict, Any, List
try:
    from .agent import Agent
except ImportError:
    from agent.agent import Agent

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
        3. 不明な点がある場合は、Manager に対して質問を行う。
        
        回答は、具体的にどのような意図でそのコードを書いたかという説明と共に、コードブロックを用いて提示してください。
        """
        instructions = """
        実装を行う際は、まず指示された要件を正しく理解しているか確認し、その後実装に入ってください。
        大規模な実装の場合は、段階的にコードを提示してください。
        """
        super().__init__(name, role, instructions)

    def execute_tool(self, tool_name: str, args: Dict[str, Any]) -> Any:
        # 今後、ファイルの作成やテストの実行などのツールを追加予定
        pass
