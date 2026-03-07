
from view.modals.server import Server
from storage import Storage
from core.server_processor import ServerProcessor
from core.addons import Addons
from configs import Config
import uuid
import logging

class ServerManager():
    def __init__(self):
        self.storage = Storage()
        self._config = Config()
        self.servers = []
        self._addons = None
        self._addonscfg = {}
        self._server_processor = ServerProcessor(terminal_type="Windows_Terminal")
        
    def validate_server(self, server: Server) -> bool:
        errors = []
        
        if not server.server_name or server.server_name.strip() == "":
            errors.append("server_name is mandatory")
        
        if not server.root_path or server.root_path.strip() == "":
            errors.append("root_path is mandatory")
        
        if not server.runnable_command or server.runnable_command.strip() == "":
            errors.append("runnable_command is mandatory")
        
        if errors:
            raise ValueError("; ".join(errors))
        
        return True

    def add_server(self, server):
        try:
            # Validate server before processing
            self.validate_server(server)
            
            # Get existing servers to determine next ID
            servers = self.storage.readAll()
            if servers:
                last_id = int(servers[-1].get('server_id', 0))
                server.server_id = str(last_id + 1)
            else:
                server.server_id = uuid.uuid4().hex
            
            self.storage.create(server)
            return True
        except ValueError as e:
            logging.error(f"SPServerManagerException::: Validation error: {e}")
            return False
        except Exception as e:
            logging.error(f"SPServerManagerException::: Error while adding server: {e}")
            return False
        
    def update_server(self, new_server_details):
        """Update server details by server ID."""
        try:
            # Validate server before processing
            self.validate_server(new_server_details)
            
            # Delegate JSON file handling to storage layer
            result = self.storage.update(new_server_details.server_id, new_server_details)
            return result
        except ValueError as e:
            logging.error(f"SPServerManagerException::: Validation error: {e}")
            return False
        except Exception as e:
            logging.error(f"SPServerManagerException::: Error while updating server: {e}")
            return False
        

    def remove_server(self, serverid):
        self.storage.delete(serverid)

    def list_servers(self):
        servers = self.storage.readAll()
        self._addons = Addons(self._config)
        self._addonscfg = self._addons.get_addons()
        for server in servers:
            # dynamically update git branch info for each server based on its root path if git integration addon is enabled
            if(self._addonscfg.get("git_integration", {}).get("enabled", False)):
                root_path = server.get('root_path')
                if root_path:
                    git_branch = self._addons.get_git_branch_name(root_path)
                    server['git_branch'] = git_branch
            # checking if server process is running and updating pid_status accordingly if server detection addon is enabled
            server_detection_cfg= self._addonscfg.get("server_detection", {})
            if (server_detection_cfg.get("enabled", False) and self._addons.is_server_process_running(server.get('server_id'))):
                server['pid_status'] = 1
        return servers
    
    def start_server(self, server_id):
        servers = self.storage.readAll()
        server = next((s for s in servers if s.get('server_id') == server_id), None)
        if server:
            self._server_processor.set_server(server).start()
        else:
            logging.warning(f"Server with ID {server_id} not found.")
            
    def stop_server(self, server_id):
        servers = self.storage.readAll()
        server = next((s for s in servers if s.get('server_id') == server_id), None)
        if server:
            self._server_processor.set_server(server).stop()
        else:
            logging.warning(f"Server with ID {server_id} not found.")
    
    def set_proxy(self, env: str) -> bool:
        
        """Set proxy configuration for a specific environment."""
        self._addons = Addons(self._config)
        self._addonscfg = self._addons.get_addons()
        if not self._addonscfg.get("proxy_settings", {}).get("enabled", False):
            logging.warning("Proxy settings are not enabled in config.")
            return False
        return self._addons._custom_addons.set_proxy_environment(env)
    
    def get_available_proxy_envs(self) -> list:
        
        """Get list of available proxy environments."""
        self._addons = Addons(self._config)
        self._addonscfg = self._addons.get_addons()
        if not self._addonscfg.get("proxy_settings", {}).get("enabled", False):
            logging.warning("Proxy settings are not enabled in config.")
            return []
        return self._addons._custom_addons.get_available_proxy_environments()
    
    def get_app_render_attributes(self):
        """Get attributes needed for app rendering, such as terminal type and addon statuses."""
        self._addons = Addons(self._config)
        self._addonscfg = self._addons.get_addons()
        logging.info(f'SPServerManager::: Fetching app render attributes with config: {self._config.server_settings}, addons config: {self._addonscfg}')
        return {
            "app_name": self._config.app_info.get("app_name", "DevDock"),
            "refresh_interval": self._config.server_settings.get("refresh_interval", 10),
            "error_reporting": self._config.server_settings.get("error_reporting", False),
            "enable_notifications": self._config.server_settings.get("enable_notifications", False),
            "addons": {
                "git_integration": self._addonscfg.get("git_integration", {}).get("enabled", False),
                "server_detection": self._addonscfg.get("server_detection", {}).get("enabled", False),
                "proxy_settings": {
                   "enabled": self._addonscfg.get("proxy_settings", {}).get("enabled", False),
                   "active_environment": self._addons._custom_addons.get_current_proxy_environment() if self._addonscfg.get("proxy_settings", {}).get("enabled", False) else None
                    },
                "environment_inspection": self._addonscfg.get("environment_inspection", {}).get("enabled", False)
            }
        }
