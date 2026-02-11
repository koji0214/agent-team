import pytest
import os
from unittest.mock import MagicMock, patch
from pathlib import Path
from agent.architect import Architect

@pytest.fixture
def mock_env():
    with patch.dict(os.environ, {'GEMINI_API_KEY': 'dummy_key'}):
        yield

@pytest.fixture
def architect(mock_env):
    with patch('google.genai.Client'):
        return Architect()

def test_architect_initialization(architect):
    assert architect.name == "Architect"
    assert "アーキテクト" in architect.role
    # ツールが登録されているか確認
    assert len(architect.tools) >= 2
    tool_names = [t.__name__ for t in architect.tools]
    assert "write_design_doc" in tool_names
    assert "list_project_files" in tool_names

def test_write_design_doc(architect, tmp_path):
    # テスト用にプロジェクトルートを一時ディレクトリに変更
    architect.project_root = tmp_path
    
    file_path = "docs/design.md"
    content = "# Design Document"
    
    result = architect.execute_tool("write_design_doc", {"file_path": file_path, "content": content})
    
    assert "Successfully saved" in result
    
    # 実際にファイルが作成されたか確認
    saved_file = tmp_path / file_path
    assert saved_file.exists()
    assert saved_file.read_text(encoding="utf-8") == content

def test_write_design_doc_outside_root(architect, tmp_path):
    architect.project_root = tmp_path
    
    # プロジェクトルート外への書き込みを試行
    file_path = "../outside.md"
    content = "malicious content"
    
    result = architect.execute_tool("write_design_doc", {"file_path": file_path, "content": content})
    
    assert "Error: Security violation" in result
    assert not (tmp_path.parent / "outside.md").exists()

def test_list_project_files(architect, tmp_path):
    architect.project_root = tmp_path
    
    # ダミーファイルの作成
    (tmp_path / "src").mkdir()
    (tmp_path / "src/main.py").touch()
    (tmp_path / "README.md").touch()
    
    result = architect.execute_tool("list_project_files", {"directory": ".", "max_depth": 2})
    
    assert "src" in result
    assert "main.py" in result
    assert "README.md" in result

def test_execute_tool_dispatch(architect):
    with patch.object(architect, 'write_design_doc') as mock_write:
        architect.execute_tool("write_design_doc", {"file_path": "test.md", "content": "test"})
        mock_write.assert_called_once_with(file_path="test.md", content="test")
        
    with patch.object(architect, 'list_project_files') as mock_list:
        architect.execute_tool("list_project_files", {"directory": "src"})
        mock_list.assert_called_once_with(directory="src")
