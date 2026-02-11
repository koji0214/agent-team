import pytest
import os
from unittest.mock import MagicMock, patch
from agent.coder import Coder

@pytest.fixture
def mock_env():
    with patch.dict(os.environ, {'GEMINI_API_KEY': 'dummy_key'}):
        yield

@pytest.fixture
def coder(mock_env):
    with patch('google.generativeai.GenerativeModel'):
        return Coder()

def test_coder_initialization(coder):
    assert coder.name == "Coder"
    assert "ソフトウェアエンジニア" in coder.role

def test_coder_build_system_prompt(coder):
    prompt = coder._build_system_prompt()
    assert "Coder" in prompt
    assert "役割:" in prompt

def test_coder_write_to_sandbox_success(coder, tmp_path):
    # sandboxディレクトリを一時ディレクトリに差し替え
    coder.sandbox_dir = tmp_path
    
    file_path = "test.txt"
    content = "Hello, Sandbox!"
    
    result = coder.write_to_sandbox(file_path, content)
    
    assert "Successfully saved" in result
    assert (tmp_path / file_path).read_text() == content

def test_coder_write_to_sandbox_security_violation(coder, tmp_path):
    coder.sandbox_dir = tmp_path
    
    # sandboxの外、例えば ../outside.txt への書き込みを試行
    file_path = "../outside.txt"
    content = "Sneaky peek"
    
    result = coder.write_to_sandbox(file_path, content)
    
    assert "Error: Security violation" in result
    # ファイルが作成されていないことを確認
    assert not (tmp_path.parent / "outside.txt").exists()
