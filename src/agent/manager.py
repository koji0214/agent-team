from typing import Dict, Any, List
from rich.console import Console

# Consoleインスタンス
console = Console()

# 相対インポートを使用（srcパッケージ内での実行を想定）
try:
    from .agent import Agent
except ImportError:
    # テスト時などのために絶対インポートへのフォールバック
    from agent.agent import Agent

class Manager(Agent):
    """
    プロジェクト全体を管理するリーダーエージェント。
    ユーザーの意図を理解し、タスクを分解し、適切なワーカーエージェントに割り当てる。
    """

    def __init__(self, name: str = "Manager"):
        role = """
        あなたはプロジェクトマネージャー兼テックリードです。
        以下の責任を持ちます：
        1. ユーザーの曖昧な要求を明確なタスクに分解する。
        2. アーキテクチャ設計が必要な場合はArchitectエージェントに依頼する。
        3. 実装が必要な場合はCoderエージェントに依頼する。
        4. 進捗を管理し、ユーザーに報告する。
        
        あなたは自分でコードを書くよりも、他のエージェントを指揮することに集中してください。
        """
        instructions = """
        ユーザーからの入力に対して、まず全体の計画を立ててください。
        必要であれば `decompose_task` ツールを使ってタスクをリスト化してください。
        """
        super().__init__(name, role, instructions)
        self.sub_agents: Dict[str, Agent] = {}

    def assign_agent(self, agent_name: str, agent: Agent):
        """
        チームメンバー（サブエージェント）を登録する。
        """
        self.sub_agents[agent_name] = agent
        console.print(f"[green]Manager assigned {agent_name} to the team.[/green]")

    def execute_tool(self, tool_name: str, args: Dict[str, Any]) -> Any:
        """
        Managerが使用できるツールを実行する。
        現在はタスク分解ツールなどを想定。
        """
        if tool_name == "decompose_task":
            return self._decompose_task(args.get("requirements", ""))
        elif tool_name == "delegate_task":
            return self._delegate_task(args.get("agent_name"), args.get("task_content"))
        else:
            return f"Error: Tool {tool_name} not found."

    def _decompose_task(self, requirements: str) -> List[str]:
        """
        【仮実装】要件をタスクに分解する。
        本来はLLMを使って分解するが、ここではスタブとして返す。
        """
        console.print(f"[bold magenta]Manager decomposing task:[/bold magenta] {requirements}")
        # TODO: LLMを使ってインテリジェントに分解する
        return ["設計を作成する", "環境を構築する", "実装する", "テストする"]

    def _delegate_task(self, agent_name: str, task_content: str) -> str:
        """
        指定されたエージェントにタスクを委譲する。
        """
        if agent_name not in self.sub_agents:
            return f"Error: Agent {agent_name} is not in the team."
        
        target_agent = self.sub_agents[agent_name]
        console.print(f"[bold yellow]Manager delegating to {agent_name}:[/bold yellow] {task_content}")
        
        # サブエージェントにメッセージを送信し、結果を受け取る
        response = target_agent.send_message(task_content)
        return f"Response from {agent_name}: {response}"
