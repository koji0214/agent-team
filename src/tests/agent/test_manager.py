import pytest
import os
from unittest.mock import MagicMock, patch
from agent.manager import Manager
from agent.agent import Agent

# 具象クラスが必要なのでAgentのダミーを作る
class DummyAgent(Agent):
    def execute_tool(self, tool_name, args):
        return "OK"

@pytest.fixture
def mock_env():
    with patch.dict(os.environ, {"GEMINI_API_KEY": "dummy"}):
        yield

@pytest.fixture
def manager(mock_env):
    with patch('google.generativeai.GenerativeModel'):
        m = Manager("Manager")
        m.chat_session = MagicMock()
        m.model = MagicMock()
        return m

@pytest.fixture
def dummy_agent(mock_env):
    with patch('google.generativeai.GenerativeModel'):
        a = DummyAgent("Coder", "Coder", "Code stuff")
        a.chat_session = MagicMock()
        a.model = MagicMock()
        return a

def test_manager_assign_agent(manager, dummy_agent):
    # チームメンバーの登録をテスト
    manager.assign_agent("Coder", dummy_agent)
    assert "Coder" in manager.sub_agents
    assert manager.sub_agents["Coder"] == dummy_agent

def test_manager_decompose_task(manager):
    # タスク分解ツールのスタブ動作確認
    args = {"requirements": "Create a login system"}
    result = manager.execute_tool("decompose_task", args)
    
    assert isinstance(result, list)
    assert "設計を作成する" in result

def test_manager_delegate_task(manager, dummy_agent):
    # タスク委譲のテスト
    manager.assign_agent("Coder", dummy_agent)
    
    # Coderエージェントのレスポンスをモック
    mock_response = MagicMock()
    mock_response.text = "Implemented login system"
    dummy_agent.chat_session.send_message.return_value = mock_response

    # 委譲を実行
    result = manager._delegate_task("Coder", "Implement login")
    
    assert "Response from Coder" in result
    assert "Implemented login system" in result
