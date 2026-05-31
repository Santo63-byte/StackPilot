
from core.server_processor import ServerProcessor
from configs import Config
import logging
import os
import subprocess

#CORE
class ProcessManager:
    """Manages the lifecycle of server processes, including starting, stopping, and tracking their status."""
    
    def __init__(self):
        self.registered_processes = {}  
        self._config = Config()
        self.terminal_type = self.get_terminal_type()
        
    def get_terminal_type(self):
        app_settings = self._config.server_settings
        self.terminal_type = app_settings.get("terminal", "StackPilot_Terminal")
        return self.terminal_type
        
    def open_advanced_terminal(self, path: str = None):
        """Open a new terminal at the specified path."""
        current_os = self._config.context.get("os", None)
        if current_os == "windows":
            if path and path.strip():
                if not os.path.isdir(path):
                    logging.error(f"Specified path does not exist or is not a directory: {path}")
                    return {"success": False, "message": f"Specified path does not exist or is not a directory: {path}"}
                subprocess.Popen(["wt", "-d", path])
            else:
                subprocess.Popen(["wt"])
            return {"success": True, "message": "Terminal opened successfully"}
        # MAC IMPL PENDING
        # elif current_os == "mac":
        #     terminal_command = f'gnome-terminal -- bash -c "cd {path}; exec bash"' if path else 'gnome-terminal'
        else:
            raise ValueError(f"Unsupported OS detected. No terminal available : {current_os}")
        
    def is_port_in_use(self, port: int):
        """Check if a given port is currently in use."""
        current_os = self._config.context.get("os", None)
        if current_os == "windows":
            command = f"netstat -ano | findstr :{port}"
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            return result.returncode == 0 and bool(result.stdout.strip())
        
        # MAC IMPL PENDING
        # elif current_os == "mac":
        else:
            raise ValueError(f"Unsupported OS detected. Cannot check port usage: {current_os}")
        
    def kill_port(self, port: int):
        """Kill the process running on the specified port."""
        current_os = self._config.context.get("os", None)
        if current_os == "windows":
            command = f"netstat -ano | findstr :{port}"
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                logging.error(f"No process found running on port {port}")
                return {"success": False, "message": f"No process found running on port {port}"}
            
            lines = result.stdout.strip().splitlines()
            if not lines:
                logging.error(f"No process found running on port {port}")
                return {"success": False, "message": f"No process found running on port {port}"}
            
            pid = lines[0].strip().split()[-1]
            kill_command = f"taskkill /PID {pid} /F"
            kill_result = subprocess.run(kill_command, shell=True, capture_output=True, text=True)
            if kill_result.returncode == 0:
                logging.info(f"Successfully killed process on port {port}")
                return {"success": True, "message": f"Successfully killed process on port {port}"}
            else:
                logging.error(f"Failed to kill process on port {port}: {kill_result.stderr}")
                return {"success": False, "message": f"Failed to kill process on port {port}: {kill_result.stderr}"}
        # MAC IMPL PENDING
        # elif current_os == "mac":
        else:
            raise ValueError(f"Unsupported OS detected. Cannot kill process by port: {current_os}")
