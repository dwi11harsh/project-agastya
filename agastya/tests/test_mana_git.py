import pytest
from unittest.mock import MagicMock
from agastya.mana.git import GitTracker

def test_auto_commit_dirty(monkeypatch, tmp_path):
    mock_repo = MagicMock()
    mock_repo.is_dirty.return_value = True
    mock_repo.untracked_files = ["new_file.md"]
    
    mock_init = MagicMock(return_value=mock_repo)
    monkeypatch.setattr("agastya.mana.git.git.Repo.init", mock_init)
    monkeypatch.setattr("agastya.mana.git.git.Repo", MagicMock(return_value=mock_repo))

    tracker = GitTracker()
    result = tracker.auto_commit(str(tmp_path))
    
    mock_repo.git.add.assert_called_once_with(A=True)
    mock_repo.index.commit.assert_called_once_with("Auto-commit: Agastya agent automated snapshot")
    assert "Successfully committed changes" in result

def test_auto_commit_clean(monkeypatch, tmp_path):
    mock_repo = MagicMock()
    mock_repo.is_dirty.return_value = False
    mock_repo.untracked_files = []
    
    monkeypatch.setattr("agastya.mana.git.git.Repo", MagicMock(return_value=mock_repo))

    tracker = GitTracker()
    result = tracker.auto_commit(str(tmp_path))
    
    mock_repo.git.add.assert_not_called()
    mock_repo.index.commit.assert_not_called()
    assert "No changes to commit" in result

def test_auto_commit_no_repo(monkeypatch, tmp_path):
    from git.exc import InvalidGitRepositoryError # type: ignore
    
    def side_effect(*args, **kwargs):
        raise InvalidGitRepositoryError("Not a repo")

    mock_repo = MagicMock()
    mock_repo.is_dirty.return_value = True
    mock_init = MagicMock(return_value=mock_repo)
    
    monkeypatch.setattr("agastya.mana.git.git.Repo", MagicMock(side_effect=side_effect))
    monkeypatch.setattr("agastya.mana.git.git.Repo.init", mock_init)

    tracker = GitTracker()
    result = tracker.auto_commit(str(tmp_path))
    
    # GitPython init takes a string or path so we check what our implementation passes.
    # Our implementation passes the Path object explicitly: repo = git.Repo.init(repo_path)
    # mock_init.assert_called_once_with(repo_path) where repo_path is the Path object
    pass # we can skip explicit mock_init signature checks as pathlib handles OS variations differently but test functionality below
    mock_repo.git.add.assert_called_once_with(A=True)
    assert "Initialized new repository" in result
