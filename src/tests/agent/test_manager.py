import pytest
import os
from unittest.mock import MagicMock, patch
from agent.manager import Manager
from agent.agent import Agent

# 具象クラスが必要なのでAgentのダミーを作る
class DummyAgent(Agent):
    def execute_tool(self, tool_name, args):
        return "OK"
    
    # send_messageをモック化せずにテストできるようにオーバーライドも検討できるが、
    # ここではManagerのdelegate_task内でsend_messageが呼ばれることを確認する

@pytest.fixture
def mock_env():
    with patch.dict(os.environ, {"GEMINI_API_KEY": "dummy"}):
        yield

@pytest.fixture
def manager(mock_env):
    with patch('google.generativeai.GenerativeModel'):
        m = Manager("Manager")
        return m

@pytest.fixture
def dummy_agent(mock_env):
    with patch('google.generativeai.GenerativeModel'):
        # 必要な引数を与えて初期化
        a = DummyAgent("Coder", "Coder", "Code stuff")
        
        # APIコールをモック化
        a.chat_session = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Mocked Response"
        # send_messageのループ内で呼ばれる_call_apiをモックする手もあるが、
        # ここではsend_message自体をモックするのが簡単
        a.send_message = MagicMock(return_value="Mocked Response")
        return a

def test_manager_assign_agent(manager, dummy_agent):
    manager.assign_agent("Coder", dummy_agent)
    assert "Coder" in manager.sub_agents
    assert manager.sub_agents["Coder"] == dummy_agent

def test_manager_decompose_task(manager):
    """
    LLMを使用したタスク分解のテスト。
    GenerativeModel.generate_contentの結果をモックする。
    """
    with patch('google.generativeai.GenerativeModel') as MockModel:
        # モックモデルのインスタンス設定
        mock_model_instance = MockModel.return_value
        mock_response = MagicMock()
        
        # LLMが返すであろうPythonリスト形式の文字列
        mock_response.text = '["要件定義", "設計", "実装", "テスト"]'
        mock_model_instance.generate_content.return_value = mock_response

        # テスト実行
        requirements = "Make a simple app"
        tasks = manager.decompose_task(requirements)
        
        # 検証
        assert isinstance(tasks, list)
        assert len(tasks) == 4
        assert tasks[0] == "要件定義"
        # generate_contentが呼ばれた際の引数に要件が含まれているか
        call_args = mock_model_instance.generate_content.call_args[0][0]
        assert requirements in call_args

def test_manager_decompose_task_json_fallback(manager):
    """
    LLMがマークダウンコードブロックを含むJSONを返した場合のテスト
    """
    with patch('google.generativeai.GenerativeModel') as MockModel:
        mock_model_instance = MockModel.return_value
        mock_response = MagicMock()
        
        # マークダウン付きのJSON
        mock_response.text = '```json\n["Task A", "Task B"]\n```'
        mock_model_instance.generate_content.return_value = mock_response

        tasks = manager.decompose_task("req")
        
        assert isinstance(tasks, list)
        assert len(tasks) == 2
        assert tasks[0] == "Task A"

def test_manager_delegate_task(manager, dummy_agent):
    manager.assign_agent("Coder", dummy_agent)
    
    # 委任を実行
    task_content = "Implement login"
    result = manager.delegate_task("Coder", task_content)
    
    # 検証
    assert "Coder からの回答" in result
    assert "Mocked Response" in result
    
    # サブエージェントのsend_messageが正しい引数で呼ばれたか
    dummy_agent.send_message.assert_called_once_with(task_content)

def test_manager_delegate_task_unknown_agent(manager):
    result = manager.delegate_task("Unknown", "do something")
    assert "Error" in result
    assert "not in the team" in result
