import pytest
import os
from pathlib import Path
from agastya.builtins.file_ops import read_file, write_file, list_dir

@pytest.fixture
def temp_workspace(tmp_path):
    return tmp_path

def test_read_file_success(temp_workspace):
    test_file = temp_workspace / "test.txt"
    test_file.write_text("Hello Agastya")
    
    assert read_file(str(test_file)) == "Hello Agastya"

def test_read_file_not_found(temp_workspace):
    missing_file = temp_workspace / "ghost.txt"
    # Should not crash but return an error string context to be fed back to LLM
    result = read_file(str(missing_file))
    assert result.startswith("Error reading file")
    assert "No such file or directory" in result

def test_write_file_success(temp_workspace):
    target = temp_workspace / "out.md"
    write_file(str(target), "# Title")
    
    assert target.exists()
    assert target.read_text() == "# Title"

def test_write_file_creates_parents(temp_workspace):
    target = temp_workspace / "deep" / "nested" / "file.txt"
    write_file(str(target), "nested data")
    
    assert target.exists()
    assert target.read_text() == "nested data"

def test_list_dir(temp_workspace):
    (temp_workspace / "file1.txt").touch()
    (temp_workspace / "file2.md").touch()
    (temp_workspace / "folder").mkdir()
    
    contents = list_dir(str(temp_workspace))
    # It should return a list of strings
    assert isinstance(contents, list)
    assert len(contents) == 3
    # Check that dir indicator is working, etc is optional but sorting is good
    assert sorted(contents) == ["file1.txt", "file2.md", "folder/"]

def test_list_dir_missing(temp_workspace):
    missing_dir = temp_workspace / "non_existent"
    result = list_dir(str(missing_dir))
    assert len(result) == 1
    assert result[0].startswith("Error listing directory")
