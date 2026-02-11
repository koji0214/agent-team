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
