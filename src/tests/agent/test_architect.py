import unittest
from unittest.mock import MagicMock, patch
from agent.architect import Architect

class TestArchitect(unittest.TestCase):
    @patch('google.generativeai.GenerativeModel')
    @patch.dict('os.environ', {'GEMINI_API_KEY': 'dummy_key'})
    def test_architect_initialization(self, mock_model):
        architect = Architect()
        self.assertEqual(architect.name, "Architect")
        self.assertIn("アーキテクト", architect.role)

    @patch('google.generativeai.GenerativeModel')
    @patch.dict('os.environ', {'GEMINI_API_KEY': 'dummy_key'})
    def test_architect_build_system_prompt(self, mock_model):
        architect = Architect()
        prompt = architect._build_system_prompt()
        self.assertIn("Architect", prompt)
        self.assertIn("役割:", prompt)

if __name__ == '__main__':
    unittest.main()
