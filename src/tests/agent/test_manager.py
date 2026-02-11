import unittest
import os
from unittest.mock import MagicMock, patch
from agent.manager import Manager
from agent.agent import Agent

class TestManager(unittest.TestCase):

    @patch.dict(os.environ, {"GEMINI_API_KEY": "dummy"})
    def setUp(self):
        # 具象クラスが必要なのでAgentのダミーを作る
        class DummyAgent(Agent):
            def execute_tool(self, tool_name, args):
                return "OK"
        
        self.manager = Manager("Manager")
        self.dummy_agent = DummyAgent("Coder", "Coder", "Code stuff")
        
        # モックを使って実行をテスト
        self.manager.chat_session = MagicMock()
        self.manager.model = MagicMock()
        self.dummy_agent.chat_session = MagicMock()
        self.dummy_agent.model = MagicMock()

    def test_assign_agent(self):
        # チームメンバーの登録をテスト
        self.manager.assign_agent("Coder", self.dummy_agent)
        self.assertIn("Coder", self.manager.sub_agents)
        self.assertEqual(self.manager.sub_agents["Coder"], self.dummy_agent)

    def test_decompose_task(self):
        # タスク分解ツールのスタブ動作確認
        args = {"requirements": "Create a login system"}
        result = self.manager.execute_tool("decompose_task", args)
        
        self.assertIsInstance(result, list)
        self.assertIn("設計を作成する", result)

    def test_delegate_task(self):
        # タスク委譲のテスト
        self.manager.assign_agent("Coder", self.dummy_agent)
        
        # Coderエージェントのレスポンスをモック
        mock_response = MagicMock()
        mock_response.text = "Implemented login system"
        self.dummy_agent.chat_session.send_message.return_value = mock_response

        # 委譲を実行
        args = {"agent_name": "Coder", "task_content": "Implement login"}
        result = self.manager._delegate_task("Coder", "Implement login")
        
        self.assertIn("Response from Coder", result)
        self.assertIn("Implemented login system", result)

if __name__ == '__main__':
    unittest.main()
