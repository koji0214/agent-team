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
        1. ユーザーの曖昧な要求を分解し、具体的なタスクリストを作成する。
        2. アーキテクチャ設計が必要な場合は `Architect` エージェントに依頼する。
        3. 実装が必要な場合は `Coder` エージェントに依頼する。
        4. 進捗を管理し、ユーザーに報告する。
        
        あなたは自分でコードを書くよりも、部下の専門エージェントを指揮することに集中してください。
        """
        instructions = """
        ユーザーからの入力に対して、まず「何が必要か」を考え、必要に応じてツールを呼び出してください。
        設計が未完了の場合は必ず Architect に設計を依頼してください。
        指示は具体的かつ簡潔に行ってください。
        """
        super().__init__(name, role, instructions, tools=[self.decompose_task, self.delegate_task])
        self.sub_agents: Dict[str, Agent] = {}

    def assign_agent(self, agent_name: str, agent: Agent):
        """
        チームメンバー（サブエージェント）を登録する。
        """
        self.sub_agents[agent_name] = agent
        console.print(f"[green]Manager assigned {agent_name} to the team.[/green]")

    def decompose_task(self, requirements: str) -> List[str]:
        """
        ユーザーの要件を具体的なタスクのリスト（文字列の配列）に分解します。
        
        Args:
            requirements (str): ユーザーからの要望や要件の記述。
            
        Returns:
            List[str]: 分解されたタスクのリスト。
        """
        console.print(f"[bold magenta]Manager thinking:[/bold magenta] Decomposing task: {requirements}")
        # 実際にはLLMに分解させたいが、今はツールとして呼ばれたこと自体をログに出す
        # 自動実行されるため、戻り値がLLMのコンテキストに戻る
        tasks = ["設計ガイドラインの作成", "基本機能の実装", "単体テストの作成"]
        console.print(f"[bold magenta]Manager result:[/bold magenta] Generated {len(tasks)} tasks.")
        return tasks

    def delegate_task(self, agent_name: str, task_content: str) -> str:
        """
        指定されたエージェントに特定のタスクを依頼し、その結果を受け取ります。
        利用可能なエージェント: Architect (設計担当)
        
        Args:
            agent_name (str): 依頼先のエージェント名。
            task_content (str): 依頼する具体的な内容。
            
        Returns:
            str: 依頼先エージェントからの回答。
        """
        if agent_name not in self.sub_agents:
            return f"Error: Agent {agent_name} is not in the team. Available agents: {list(self.sub_agents.keys())}"
        
        target_agent = self.sub_agents[agent_name]
        console.print(f"[bold yellow]Manager to {agent_name}:[/bold yellow] {task_content}")
        
        # サブエージェントにメッセージを送信し、結果を受け取る
        # ここで別のエージェントの send_message が呼ばれ、再帰的に思考が走る
        response = target_agent.send_message(task_content)
        return f"{agent_name} からの回答: {response}"

    def execute_tool(self, tool_name: str, args: Dict[str, Any]) -> Any:
        """
        自動関数呼び出しを使用するため、手動実行が必要な場合のみ使用。
        """
        if tool_name == "decompose_task":
            return self.decompose_task(**args)
        elif tool_name == "delegate_task":
            return self.delegate_task(**args)
        return f"Tool {tool_name} not found."
