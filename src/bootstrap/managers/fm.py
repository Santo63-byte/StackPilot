import logging
from logging.handlers import TimedRotatingFileHandler
import json
import os


class FileManager:
    def __init__(self, context:object=None, config:object=None):
            self._config = config
            self._context = context
            
    FOLDERS = ["logs", "data", "sessions", "backups"]
    
    def _create_parent_folders(self, base_path: str) -> None:
        """Create parent folders required by the application."""
        
        for folder in self.FOLDERS:
            folder_path = os.path.join(base_path, folder)
            
            if not os.path.exists(folder_path):
                os.makedirs(folder_path, exist_ok=True)
                logging.info(f"Created folder: '{folder_path}'")
                
    def setup_files(self) -> None:
        """Setup necessary files and directories."""
        #creating parent folders
        storage_path = f'{self._config.server_settings.get("storage")}/{self._config.app_info.get("app_name","StackPilot")}'
        if storage_path and not os.path.exists(storage_path):
            os.makedirs(storage_path, exist_ok=True)
            logging.info(f"Created datasource path: '{storage_path}'")
        self._create_parent_folders(storage_path)
        self.create_log_file(storage_path)
        self._create_data_files() # store data files like serverlist etc
        
    def create_log_file(self, path) -> None:
        """Configure application logging with daily rotation."""
        try:
            logs_path = os.path.join(path, "logs")
            
            # Ensure logs directory exists
            if not os.path.exists(logs_path):
                os.makedirs(logs_path, exist_ok=True)
            
            log_file_path = os.path.join(logs_path, "app.log")
            
            # Create logger
            logger = logging.getLogger()
            logger.setLevel(logging.INFO)
            
            # Remove existing handlers to avoid duplicates
            for handler in logger.handlers[:]:
                logger.removeHandler(handler)
            
            # Create TimedRotatingFileHandler for daily rotation
            # when="midnight" creates new log file at midnight
            # interval=1 means every 1 day
            # backupCount keeps last 30 days of logs
            handler = TimedRotatingFileHandler(
                filename=log_file_path,
                when="midnight",
                interval=1,
                backupCount=30,
                encoding='utf-8'
            )
            
            # Set format
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logging.info(f"Logging configured. Log files will be created in: '{logs_path}'")
            logging.info("Daily rotation enabled. Backup count: 30 days")
            
        except Exception as e:
            logging.error(f"Error configuring logging: {e}")
        
    def _get_defaults_server_data(self):
        """Get default content for server data file."""
        default_content = {
            "server_id": "1",
            "port_no": self._config.app_info.get("port", 8000),
            "root_path": self._config.server_settings.get("storage", "C_Drive_Temp)"),
            "runnable_command": "python stackpilotapp.py",
            "git_branch": "unknown",
            "server_name": self._config.app_info.get("app_name", "StackPilot"),
            "pid_status":1
        }
        return default_content
    
    def create_process_registry_file(self) -> None:
        """Create process registry file if it doesn't exist."""
        storage_path = f'{self._config.server_settings.get("storage")}/{self._config.app_info.get("app_name","StackPilot")}'
        registry_file_path = os.path.join(storage_path, "process_registry.json")
        self._context["datasources"]["process_registry"] = registry_file_path 
        if not os.path.exists(registry_file_path):
            try:
                with open(registry_file_path, 'w') as f:
                    json.dump({}, f, indent=4)
                logging.info(f"Created process registry file: '{registry_file_path}'")
            except Exception as e:
                logging.error(f"Error creating process registry file: {e}")
                
        else:
            logging.info(f"Process registry file already exists: '{registry_file_path}'")
            
    def create_server_data_file(self) -> None:
        """Create server data file with default content if it doesn't exist."""
        SERVER_LIST: str = "serverslist.json"
        root_path = f"{self._config.server_settings.get('storage')}/{self._config.app_info.get('app_name','StackPilot')}/data"
        file_path = os.path.join(root_path, SERVER_LIST)
        self._context["datasources"]["server_list"] = file_path  # Update config with actual path used
        # Get default server data
        default_server = self._get_defaults_server_data()
        
        # Create the JSON structure with server_lists as array
        file_structure = {
            "default_user": {
                "server_lists": [default_server]
            }
        }
        
        # Check if file exists and is not empty
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            try:
                # File exists, read it and replace/update server with server_id = "1"
                with open(file_path, 'r') as f:
                    existing_data = json.load(f)
                
                # Ensure server_lists exists
                if "default_user" not in existing_data:
                    existing_data["default_user"] = {}
                if "server_lists" not in existing_data["default_user"]:
                    existing_data["default_user"]["server_lists"] = []
                
                # Find and replace server with server_id = "1", or add if not found
                server_lists = existing_data["default_user"]["server_lists"]
                found = False
                for i, server in enumerate(server_lists):
                    if server.get("server_id") == "1":
                        server_lists[i] = default_server
                        found = True
                        break
                if not found:
                    server_lists.append(default_server)
                with open(file_path, 'w') as f:
                    json.dump(existing_data, f, indent=4)
                logging.info(f"Updated server data file: '{file_path}'")
            except Exception as e:
                logging.error(f"Error updating server data file: {e}")
        else:
            # File doesn't exist or is empty, create new file
            try:
                with open(file_path, 'w') as f:
                    json.dump(file_structure, f, indent=4)
                logging.info(f"Created server data file: '{file_path}'")
            except Exception as e:
                logging.error(f"Error creating server data file: {e}")
        
    def _create_data_files(self) -> None:
        """Create a data file with default content if it doesn't exist."""
        self.create_server_data_file()
        self.create_process_registry_file()
