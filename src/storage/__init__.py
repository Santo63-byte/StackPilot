
from core.abstracts.crud import CRUD
from typing import  Optional, override
from configs import Config
import json
import logging

class Storage(CRUD):
   
    def __init__(self):  
        self.config = Config()
    
    def _get_context(self):
        """Get the app context."""
        return self.config.context
    
    @override
    def create(self, data) -> None:
        """Create a new record in storage."""
        context = self._get_context()
        data_resources = context.get("datasources", {})
        file_path = data_resources.get("server_list")
        
        try:
            # Read existing data
            with open(file_path, 'r') as f:
                file_data = json.load(f)
            
            user_session = "default_user"
            if user_session not in file_data:
                file_data[user_session] = {"server_lists": []}
            
            # Convert Server object to dict if needed
            if hasattr(data, 'to_dict'):
                server_dict = data.to_dict()
            else:
                server_dict = data
            
            # Add new server to the list
            file_data[user_session]["server_lists"].append(server_dict)
            
            # Write updated data back to file
            with open(file_path, 'w') as f:
                json.dump(file_data, f, indent=4)
        except Exception as e:
            logging.error(f"Error creating server in storage: {e}")
            raise
    
    @override
    def readAll(self,user_session = "default_user", id: str = None):
        """Read all servers from storage."""
        context = self._get_context()
        data_resources = context.get("datasources", {})
        if not data_resources:
            logging.warning("No data sources found in context.")
            return []
        file_path = data_resources["server_list"]
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Extract servers from the default_user session (as per current design only one session is supported)
            servers = data.get(user_session, {}).get("server_lists", [])
            return servers
        except FileNotFoundError:
            logging.error(f"Server list file not found: {file_path}")
            return []
        except json.JSONDecodeError:
            logging.error(f"Error decoding JSON from: {file_path}")
            return []
        except Exception as e:
            logging.error(f"Error reading servers: {e}")
            return []
    
    @override
    def update(self, id: str, data) -> bool:
        """Update a record in storage by ID."""
        context = self._get_context()
        data_resources = context.get("datasources", {})
        file_path = data_resources.get("server_list")
        
        try:
            # Read existing data
            with open(file_path, 'r') as f:
                file_data = json.load(f)
            
            user_session = "default_user"
            if user_session not in file_data:
                logging.warning(f"User session '{user_session}' not found")
                return False
            
            # Convert Server object to dict if needed
            if hasattr(data, 'to_dict'):
                server_dict = data.to_dict()
            else:
                server_dict = data
            
            server_id = server_dict.get("server_id")
            if not server_id:
                logging.error("Server ID is required for update")
                return False
            
            # Find and update the server with the given ID
            servers = file_data[user_session].get("server_lists", [])
            updated = False
            
            for i, server in enumerate(servers):
                if str(server.get("server_id")) == str(server_id):
                    servers[i] = server_dict
                    updated = True
                    break
            
            if not updated:
                logging.warning(f"Server with ID '{server_id}' not found")
                return False
            
            # Write updated data back to file
            with open(file_path, 'w') as f:
                json.dump(file_data, f, indent=4)
            
            logging.info(f"Server with ID '{server_id}' updated successfully")
            return True
        except Exception as e:
            logging.error(f"Error updating server in storage: {e}")
            return False
    
    @override
    def delete(self, id: str) -> None:  
        """Delete a record from storage by ID."""
        context = self._get_context()
        data_resources = context.get("datasources", {})
        file_path = data_resources.get("server_list")
        
        try:
            # Read existing data
            with open(file_path, 'r') as f:
                file_data = json.load(f)
            
            user_session = "default_user"
            if user_session not in file_data:
                logging.warning(f"User session '{user_session}' not found")
                return
            
            # Find and remove the server with the given ID
            servers = file_data[user_session].get("server_lists", [])
            original_length = len(servers)
            
            file_data[user_session]["server_lists"] = [
                server for server in servers 
                if str(server.get("server_id")) != str(id)
            ]
            
            # Check if server was found and deleted
            if len(file_data[user_session]["server_lists"]) == original_length:
                logging.warning(f"Server with ID '{id}' not found")
                return
            
            # Write updated data back to file
            with open(file_path, 'w') as f:
                json.dump(file_data, f, indent=4)
                
            logging.info(f"Server with ID '{id}' deleted successfully")
        except Exception as e:
            logging.error(f"Error deleting server from storage: {e}")
            raise
    
    def getAppConfig(self) -> Optional[dict]:
        """Get application configuration."""
        return self.configresolver.resolve()
