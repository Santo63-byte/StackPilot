import git
import os
import psutil
import logging
from core.server_processor import ProcessRegistry

#CORE
class EnvInspector:
    def __init__(self):
        self.process_registry = ProcessRegistry()
    
    def get_git_branch_name(self, repo_path: str = None):
        """Retrieve Git repository information."""
        try:
            repo = git.Repo(repo_path or os.getcwd(), search_parent_directories=True)
            return repo.active_branch.name
        except Exception as e:
            logging.error(f"EnvInspectorException::: Error retrieving Git info: {e}")
            return "unknown"

    def is_file_path_valid(self, file_path: str) :
        """Check if the given file path exists and is a file."""
        return bool(file_path) and os.path.exists(file_path)
