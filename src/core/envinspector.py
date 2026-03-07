import git
import os
import psutil
import logging
from core.server_processor import ProcessRegistry

class EnvInspector:
    def __init__(self):
        self.process_registry = ProcessRegistry()
    
    def get_git_branch_name(self, repo_path: str = None) -> str:
        """Retrieve Git repository information."""
        try:
            repo = git.Repo(repo_path or os.getcwd(), search_parent_directories=True)
            return repo.active_branch.name
        
        except Exception as e:
            logging.error(f"EnvInspectorException::: Error retrieving Git info: {e}")
            return "unknown"
         
    def is_process_running(self, pid: int) -> bool:
        """Check if a process with the given PID is running."""
        try:
            process = psutil.Process(pid)
            logging.info(f"EnvInspector::: Checking process with PID {pid}. Process info: {process.as_dict(attrs=['pid', 'name', 'status'])}")
            return process.is_running()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return False
    
    def is_server_process_running(self, server_id: str) -> bool:
        """Check if the process associated with the given server_id is running."""
        self.process_registry.get_process_registry()
        pid = self.process_registry.registered_processes.get(server_id)
        logging.info(f"EnvInspector::: Checking if server with ID {server_id} is running. Found PID: {pid}")
        
        if not pid:
            logging.info(f"EnvInspector::: No PID found for server {server_id}")
            return False
        
        if self.is_process_running(pid):
            logging.info(f"EnvInspector::: Server with ID {server_id} is currently running.")
            return True
        else:
            logging.info(f"EnvInspector::: PID {pid} not found. Checking all running processes...")
            # Debug: List all running processes to see what's available
            for proc in psutil.process_iter(['pid', 'name']):
                if 'wt.exe' in proc.info['name'].lower() or 'windowsterminal' in proc.info['name'].lower():
                    logging.info(f"EnvInspector::: Found Terminal process: PID {proc.info['pid']}, Name: {proc.info['name']}")
        return False
    
    def set_proxy(self, env , proxyfile, variable_name):
        """Set proxy configuration for a specific environment."""
        # This is a placeholder implementation. You can expand this to handle different environments and proxy configurations.
        logging.info(f"Setting proxy for environment: {env} with config: {proxyfile}")
