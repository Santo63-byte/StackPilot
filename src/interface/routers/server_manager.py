
from typing import Any, List

from view.modals.server import Server
from storage import ServerStorage
from core.server_processor import ServerProcessor
from core.process_manager import ProcessManager
from core.addons import Addons
from configs import Config
from view.modals.basemodals import BatchStartRequest
import uuid
import logging
import time

class ServerManager():
    def __init__(self):
        self.storage = ServerStorage()
        self._config = Config()
        self.servers = []
        self._addons = None
        self._addonscfg = {}
        self._processmanager= ProcessManager()
        
        
    def validate_server(self, server: Server):
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

    def _validate_server_dict(self, server: dict) -> list:
        """Validate a server dict and return a list of error messages."""
        errors = []
        if not server.get("server_name", "").strip():
            errors.append("server_name is mandatory")
        if not server.get("root_path", "").strip():
            errors.append("root_path is mandatory")
        if not server.get("runnable_command", "").strip():
            errors.append("runnable_command is mandatory")
        return errors

    def add_server(self, server, session_id=None):
        try:
            # Validate server before processing
            self.validate_server(server)
            # Get all servers globally to determine next ID
            server.server_id = uuid.uuid4().hex
            self.storage.create(server, session_id)
            return True
        except ValueError as e:
            logging.error(f"SPServerManagerException::: Validation error: {e}")
            return False
        except Exception as e:
            logging.error(f"SPServerManagerException::: Error while adding server: {e}")
            return False
        
    def update_server(self, new_server_details, session_id=None):
        """Update server details by server ID."""
        try:
            # Validate server before processing
            self.validate_server(new_server_details)
            # Delegate JSON file handling to storage layer
            result = self.storage.update(new_server_details.server_id, new_server_details, session_id)
            return result
        except ValueError as e:
            logging.error(f"SPServerManagerException::: Validation error: {e}")
            return False
        except Exception as e:
            logging.error(f"SPServerManagerException::: Error while updating server: {e}")
            return False
        
    def delete_servers(self, server_ids: List[Any], session_id=None):
        """Delete multiple servers by their IDs."""
        try:
            for server_id in server_ids:
                self.storage.delete(server_id, session_id)
            logging.info(f"Batch deleted servers with IDs: {server_ids} from session '{session_id}'")
            return True
        except Exception as e:
            logging.error(f"Error during batch delete of servers with IDs {server_ids} from session '{session_id}': {e}")
            return False

    def list_servers(self, sessionid=None):
        servers = self.storage.readAll(sessionid)
        self._addons = Addons(self._config)
        self._addonscfg = self._addons.get_addons()
        for server in servers:
            # dynamically update git branch info for each server based on its root path if git integration addon is enabled
            if(self._addonscfg.get("git_integration", {}).get("enabled", False)):
                root_path = server.get('root_path')
                if root_path:
                    git_branch = self._addons.get_git_branch_name(root_path)
                    server['git_branch'] = git_branch
                    
            self._addons.append_warnings(server)
        return servers
    
    def start_server(self, server_id, session_name=None):
        servers = self.storage.readAll(session_name)
        server = next((s for s in servers if s.get('server_id') == server_id), None)
        if not server:
            logging.warning(f"Server with ID {server_id} not found.")
            return { "success": False, "message": f"Server with ID {server_id} not found." }
        errors = self._validate_server_dict(server)
        if errors:
            logging.error(f"Validation failed for server '{server_id}': {errors}")
            return { "success": False, "message": "; ".join(errors) }
        self._server_processor = ServerProcessor(self._config, self._processmanager.get_terminal_type())
        started = self._server_processor.set_server(server).start()
        if started:
            return { "success": True, "message": None }
        return { "success": False, "message": f"Failed to start server '{server.get('server_name')}'. Check logs for details." }

    def move_servers(self, movable_server_ids:List[Any], source_session_id, target_session_id):
        
        """Move servers by their IDs from source session to target session."""
        servers = self.storage.readAll(source_session_id)

        servers_to_move = [s for s in servers if s.get('server_id') in movable_server_ids]
        if not servers_to_move:
            logging.warning(f"No servers found with IDs: {movable_server_ids} in session '{source_session_id}'.")
            return False

        # Remove from source session
        for s in servers_to_move:
            self.storage.delete(s.get('server_id'), source_session_id)

        # Add to target session
        for s in servers_to_move:
            self.storage.create(s, target_session_id)

        logging.info(f"Moved servers with IDs: {movable_server_ids} from session '{source_session_id}' to session '{target_session_id}'.")
        return True
    
    def copy_servers(self, copyable_server_ids:List[Any], source_session_id, target_session_id):
        """Copy servers by their IDs from source session to target session."""
        servers = self.storage.readAll(source_session_id)

        servers_to_copy = [s for s in servers if s.get('server_id') in copyable_server_ids]
        if not servers_to_copy:
            logging.warning(f"No servers found with IDs: {copyable_server_ids} in session '{source_session_id}'.")
            return False
        for s in servers_to_copy:
            s_copy = s.copy()
            s_copy['server_id'] = uuid.uuid4().hex 
            self.storage.create(s_copy, target_session_id)

        logging.info(f"Copied servers with IDs: {copyable_server_ids} from session '{source_session_id}' to session '{target_session_id}'.")
        return True
        
    def batch_start_servers(self, batches: BatchStartRequest, sessionid=None):
        """Start multiple servers by their IDs."""
        for i, server_id in enumerate(batches.server_ids):
            logging.info(f"Starting server with ID: {server_id}")
            self.start_server(server_id)
            if i < len(batches.server_ids) - 1:
                time.sleep(batches.delay_seconds)
        
    def stop_server(self, server_id, sessionid=None):
        servers = self.storage.readAll()
        server = next((s for s in servers if s.get('server_id') == server_id), None)
        if server:
            self._server_processor = ServerProcessor(self._config, self._processmanager.get_terminal_type())
            self._server_processor.set_server(server).kill()
        else:
            logging.warning(f"Server with ID {server_id} not found.")
    
    def set_proxy(self, env: str):
        """Set proxy configuration for a specific environment."""
        self._addons = Addons(self._config)
        self._addonscfg = self._addons.get_addons()
        if not self._addonscfg.get("proxy_settings", {}).get("enabled", False):
            logging.warning("Proxy settings are not enabled in config.")
            return False
        return self._addons._custom_addons.set_proxy_environment(env)
    
    def get_available_proxy_envs(self):
        """Get list of available proxy environments."""
        self._addons = Addons(self._config)
        self._addonscfg = self._addons.get_addons()
        if not self._addonscfg.get("proxy_settings", {}).get("enabled", False):
            logging.warning("Proxy settings are not enabled in config.")
            return []
        return self._addons._custom_addons.get_available_proxy_environments()
    
    def start_proxy(self):
        """Start the proxy server if proxy settings are enabled."""
        self._addons = Addons(self._config)
        self._addonscfg = self._addons.get_addons()
        if not self._addonscfg.get("proxy_settings", {}).get("enabled", False):
            logging.warning("Proxy settings are not enabled in config.")
            return False
        return self._addons._custom_addons.start_proxy()
    
   
