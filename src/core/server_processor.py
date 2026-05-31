from typing import Dict, List, Optional,override
from view.modals.server import Server
from configs import Config
from core.abstracts.processor import Processor
from core.utils.sltc import SLTC
import random
import os
import subprocess
import json
import logging


#CORE
class ProcessRegistry(SLTC):
    def __init__(self):
        self._context = None
        self._config = Config()
        self.registered_processes: Dict[str, any] = {}
        
    def get_process_registry(self):
        """Get the current process registry from storage."""
        self._context = self._config.context
        data_resources = self._context.get("datasources", {})
        logging.info(f"ProcessRegistry::: Current data resources in context: {data_resources}")
        registry_file_path = data_resources.get("process_registry")        
        try:
            with open(registry_file_path, 'r') as f:
                self.registered_processes = json.load(f)
        except Exception as e:
            logging.error(f"Error loading process registry: {e}")
            self.registered_processes = {}
        return self.registered_processes
    
    
    def write_process_registry(self):
        """Write the current process registry to storage."""
        data_resources = self._context.get("datasources", {})
        registry_file_path = data_resources.get("process_registry")
        logging.info(f"ProcessRegistry::: Writing process registry to: {registry_file_path} with data: {self.registered_processes}")
        try:
            with open(registry_file_path, 'w') as f:
                json.dump(self.registered_processes, f, indent=4)
        except Exception as e:
            logging.error(f"Error writing process registry: {e}")
            
            
    def register_process(self, server_name: str, process: any):
        """Register a new process with the given server_id and pid."""
        # self.registered_processes = self.get_process_registry()  # Refresh registry from storage
        self.registered_processes[server_name] = process
        #self.write_process_registry()
        
        
    def unregister_process(self, server_id: str):
        """Unregister the process associated with the given server_id."""
        self.registered_processes = self.get_process_registry()  # Refresh registry from storage
        if server_id in self.registered_processes:
            del self.registered_processes[server_id]
            self.write_process_registry()
    
    def get_registered_processes(self):
        """Get a dictionary of all registered processes with their server_id and pid."""
        return self.get_process_registry()
    
    def is_running_process(self, server_id: str):
        """Check if a process with the given server_id is currently running."""
        self.registered_processes = self.get_process_registry()  # Refresh registry from storage
        if server_id in self.registered_processes:
            return True  
        return False


#CORE
class ProcessorUtils:
    @staticmethod
    def build_command(terminal_type:str,server: dict):
        
        if terminal_type =="Windows_Terminal":
                command = ProcessorUtils.build_windows_terminal_command(server, for_new_tab=True)
                full_command = f'wt -w 0 nt {command}'
                return full_command
            
        elif terminal_type == "StackPilot_Terminal":
            """UI Stream implementation ."""
            return ProcessorUtils.build_command_for_stackpilot_terminal(server)
            
        else:
            raise ValueError(f"Unsupported terminal type: {terminal_type}. Please change terminal type in settings.")
    
    @staticmethod
    def build_command_for_stackpilot_terminal(server: dict):
        command = server["runnable_command"]
        return f"{command}"
    
        
    @staticmethod
    def build_windows_terminal_command(server:dict, for_new_tab=False):
        colors = [
        "blue", "red", "green", "yellow", "purple", "orange", "teal", "pink", "cyan", "magenta"
    ]
        color = random.choice(colors)
        project_path = server["root_path"]
        command = server["runnable_command"]
        tab_title = server.get("server_name")
        
        if not os.path.isdir(project_path):
            raise FileNotFoundError(f"Server Root path does not exist in your system: {project_path}")
        
        base = (
            f'--title "{tab_title}" '
            f'--tabColor {color} '
            f'--suppressApplicationTitle '
            f'cmd /c "cd /d {project_path} && {command} & exit"'
        )
        if not for_new_tab:
            return f'wt {base}'
        return base

#CORE
class ServerProcessor(Processor):
    def __init__(self, config:Config,terminal_type: Optional[str] = None):
        self.processor_utils = ProcessorUtils()
        self._config = config
        self.terminal_type = terminal_type 
        self.server = None
        self.process = None
        self.process_registry = ProcessRegistry()
    
    def set_server(self, server: dict):
        self.server = server
        return self
    
    def get_terminal_type(self):
        return self.terminal_type
    
    def set_terminal_type(self, terminal_type: str):
        self.terminal_type = terminal_type
        return self
    
    @override
    def start(self):
        """Start a server."""
        try:
            logging.error(f"Starting server with config: {self.server} using terminal type: {self.terminal_type}")
            if not self.server:
                raise ValueError("No server configuration provided")
            # Validate mandatory fields definitiojn
            required_fields = ["server_name", "root_path", "runnable_command"]
            for field in required_fields:
                if field not in self.server or not self.server[field]:
                    raise ValueError(f"Missing mandatory field: {field}")
                
            command = self.processor_utils.build_command(self.terminal_type, self.server)
            popen_kwargs = {"shell": True}

            if self.terminal_type == "StackPilot_Terminal":
                popen_kwargs.update({
                    "stdout": subprocess.PIPE,
                    "stderr": subprocess.STDOUT,
                    "cwd": self.server["root_path"],
                    "text": True,
                    "encoding": "utf-8",
                    "errors": "replace",
                })

            self.process = subprocess.Popen(command, **popen_kwargs)
            self.process_registry.register_process(self.server["server_name"], self.process) 
            logging.info(f"Server '{self.server['server_name']}' started successfully")
            return True
            
        except Exception as e:
            logging.error(f"Error starting server: {e}")
            return False
    
    @override
    def kill(self):
        """Kill a server process by PID."""
        try:
            if not self.server:
                raise ValueError("No server configuration provided")
            pid = self.server.get("pid_status")
            if not pid:
                logging.warning(f"No PID found for server '{self.server.get('server_name')}'. Server may not be running.")
                return False
            subprocess.run(f"taskkill /PID {pid} /F", shell=True, check=False)
            logging.info(f"Server '{self.server['server_name']}' (PID: {pid}) stopped successfully")
            return True
        except Exception as e:
            logging.error(f"Error stopping server: {e}")
            return False
    
    @override
    def restart(self):
        raise NotImplementedError("Restart functionality is not implemented yet. Please implement stop and start logic in sequence for now.")
