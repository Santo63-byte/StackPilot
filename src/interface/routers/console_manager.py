from configs import Config
from core.process_manager import ProcessManager
import logging


class ConsoleManager:
    def __init__(self):
        self._config = Config()
        self.process_manager = ProcessManager()
        
    def open_advanced_terminal(self, path: str = None):
        """Open a new terminal at the specified path."""
        result = self.process_manager.open_advanced_terminal(path)
        if not result.get("success", False):
            logging.error(f"Failed to open terminal: {result.get('message')}")
            return {"status": 500, "message": result.get("message")}
        return {"status": 200, "message": "Terminal opened successfully"}
    
    def kill_port(self, port: int):
        """Kill the process running on the specified port."""
        result = self.process_manager.kill_port(port)
        if not result.get("success", False):
            logging.error(f"Failed to kill process on port {port}: {result.get('message')}")
            return {"status": 500, "message": result.get("message")}
        return {"status": 200, "message": f"Successfully killed process on port {port}"}
