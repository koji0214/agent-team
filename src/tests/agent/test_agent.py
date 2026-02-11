import unittest
import os
from unittest.mock import MagicMock, patch
from agent.agent import Agent

class TestAgent(unittest.TestCase):

    @patch.dict(os.environ, {"GEMINI_API_KEY": "dummy"})
    def setUp(self):
        # 抽象クラスなので、テスト用に具象クラスを作成
        class ConcreteAgent(Agent):
            def execute_tool(self, tool_name, args):
                return f"Executed {tool_name} with {args}"
        
        # モックの設定
        with patch('google.generativeai.GenerativeModel') as mock_model:
            self.mock_chat = MagicMock()
            mock_model.return_value.start_chat.return_value = self.mock_chat
            self.agent = ConcreteAgent("TestBot", "Tester", "Just testing")

    def test_init(self):
        self.assertEqual(self.agent.name, "TestBot")
        self.assertEqual(self.agent.role, "Tester")
        self.assertEqual(self.agent.model_name, "gemini-2.0-flash")

    def test_send_message(self):
        # Gemini APIのレスポンスをモック
        mock_response = MagicMock()
        mock_response.text = "Hello from Gemini"
        self.mock_chat.send_message.return_value = mock_response

        response = self.agent.send_message("Hello")
        
        self.assertEqual(response, "Hello from Gemini")
        self.mock_chat.send_message.assert_called_with("Hello")

if __name__ == '__main__':
    unittest.main()
