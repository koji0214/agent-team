import pytest
import os
from unittest.mock import MagicMock, patch
from agent.architect import Architect

@pytest.fixture
def mock_env():
    with patch.dict(os.environ, {'GEMINI_API_KEY': 'dummy_key'}):
        yield

@pytest.fixture
def architect(mock_env):
    with patch('google.generativeai.GenerativeModel'):
        return Architect()

def test_architect_initialization(architect):
    assert architect.name == "Architect"
    assert "アーキテクト" in architect.role

def test_architect_build_system_prompt(architect):
    prompt = architect._build_system_prompt()
    assert "Architect" in prompt
    assert "役割:" in prompt
