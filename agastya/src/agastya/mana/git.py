import git
from pathlib import Path

class GitTracker:
    """
    Automates pushing isolated state configurations quietly tracking local snapshot history across mana documents natively.
    """
    def auto_commit(self, path: str) -> str:
        try:
            repo_path = Path(path)
            if not repo_path.exists() or not repo_path.is_dir():
                return f"Error: '{path}' is not a valid directory for tracking."

            repo_was_initialized = False
            try:
                # Try locating existing local repository within the path scope
                repo = git.Repo(repo_path)
            except git.exc.InvalidGitRepositoryError: # type: ignore
                # Does not exist, initialize a bare tree structurally here
                repo = git.Repo.init(repo_path)
                repo_was_initialized = True

            has_changes = repo.is_dirty(untracked_files=True) or bool(repo.untracked_files)
            
            if not has_changes:
                return "No changes to commit."

            # Automatically inject modifications across the localized directory via `add .` equivalent natively
            repo.git.add(A=True)
            repo.index.commit("Auto-commit: Agastya agent automated snapshot")

            status = "Initialized new repository and committed." if repo_was_initialized else "Successfully committed changes."
            return status

        except Exception as e:
            return f"Error performing auto-commit: {e}"
