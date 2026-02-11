import pytest
import os
from unittest.mock import MagicMock, patch
from agent.agent import Agent

# 抽象クラスAgentをテストするための具象クラス
class ConcreteAgent(Agent):
    def execute_tool(self, tool_name, args):
        return f"Executed {tool_name} with {args}"

@pytest.fixture
def mock_genai():
    with patch('google.genai.Client') as mock_client:
        mock_chat = MagicMock()
        mock_client.return_value.chats.create.return_value = mock_chat
        yield mock_chat

@pytest.fixture
def agent(mock_genai):
    with patch.dict(os.environ, {"GEMINI_API_KEY": "dummy"}):
        return ConcreteAgent("TestBot", "Tester", "Just testing")

def test_agent_init(agent):
    assert agent.name == "TestBot"
    assert agent.role == "Tester"
    expected_model = os.getenv("GEMINI_MODEL_NAME", "gemini-1.5-flash")
    assert agent.model_name == expected_model

def test_agent_send_message(agent, mock_genai):
    # Gemini APIのレスポンスをモック
    mock_response = MagicMock()
    mock_response.text = "Hello from Gemini"
    mock_response.candidates = [MagicMock()]
    mock_response.candidates[0].content.parts = []
    mock_genai.send_message.return_value = mock_response

    response = agent.send_message("Hello")
    
    assert response == "Hello from Gemini"
    mock_genai.send_message.assert_called_with("Hello")
