
from core.abstracts.crud import CRUD
from typing import  override
from configs import Config
import json
import logging

class ServerStorage(CRUD):
   
    NO_SESSION_DEFAULT = "spdefault"
    def __init__(self):  
        self.config = Config()
    
    def _get_context(self):
        """Get the app context."""
        return self.config.context
    
    def _get_file_path(self):
        """Get the server list file path from context."""
        context = self._get_context()
        data_resources = context.get("datasources", {})
        return data_resources.get("server_list")
    
    @override
    def create(self, data, session_id=None) -> None:
        """Create a new record in storage."""
        file_path = self._get_file_path()
        
        try:
            # Read existing data
            with open(file_path, 'r') as f:
                file_data = json.load(f)
            
            user_session = "default_user" # As per current design, we have single user support.
            if user_session not in file_data:
                file_data[user_session] = {"server_lists": []}
            
            # Convert Server object to dict if needed
            if hasattr(data, 'to_dict'):
                server_dict = data.to_dict()
            else:
                server_dict = data

            # Find the target session and add server to its servers list
            server_lists = file_data[user_session]["server_lists"]
            target_session = next((s for s in server_lists if s.get("session_id") == session_id), None)
            if target_session is None:
                logging.warning(f"Session '{session_id}' not found, server not added.")
                return
            target_session.setdefault("servers", []).append(server_dict)
            
            # Write updated data back to file
            with open(file_path, 'w') as f:
                json.dump(file_data, f, indent=4)
        except Exception as e:
            logging.error(f"Error creating server in storage: {e}")
            raise
    
    @override
    def readAll(self, session_id=None):
        """Read all servers from storage."""
        file_path = self._get_file_path()
        if not file_path:
            logging.warning("No data sources found in context.")
            return []
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            user_key = "default_user"  # As per current design, single user support
            server_lists = data.get(user_key, {}).get("server_lists", [])
            
            if session_id:
                # Return servers for the specific session
                for session in server_lists:
                    if session.get("session_id") == session_id:
                        logging.info(f"Fetching servers for session id: {session_id}")
                        return session.get("servers", [])
                logging.warning(f"Session '{session_id}' not found for user '{user_key}'")
                return []
            else:
                # No session_id — return all servers from all sessions (flattened)
                all_servers = []
                for session in server_lists:
                    all_servers.extend(session.get("servers", []))
                return all_servers
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
    def update(self, id: str, data, session_id=None) -> bool:
        """Update a record in storage by ID."""
        file_path = self._get_file_path()
        
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
            
            server_id = server_dict.get("server_id") if isinstance(server_dict, dict) else id
            if not server_id:
                logging.error("Server ID is required for update")
                return False
            
            # Find and update the server within the correct session's servers list
            server_lists = file_data[user_session].get("server_lists", [])
            updated = False
            for session in server_lists:
                if session_id and session.get("session_id") != session_id:
                    continue
                servers = session.get("servers", [])
                for i, server in enumerate(servers):
                    if str(server.get("server_id")) == str(server_id):
                        servers[i] = server_dict
                        updated = True
                        break
                if updated:
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
    def delete(self, id: str, session_id=None) -> None:  
        """Delete a record from storage by ID."""
        file_path = self._get_file_path()
        
        try:
            # Read existing data
            with open(file_path, 'r') as f:
                file_data = json.load(f)
            
            user_session = "default_user"
            if user_session not in file_data:
                logging.warning(f"User session '{user_session}' not found")
                return
            
            # Find and remove the server from the correct session's servers list
            server_lists = file_data[user_session].get("server_lists", [])
            deleted = False
            for session in server_lists:
                if session_id and session.get("session_id") != session_id:
                    continue
                servers = session.get("servers", [])
                original_length = len(servers)
                session["servers"] = [s for s in servers if str(s.get("server_id")) != str(id)]
                if len(session["servers"]) < original_length:
                    deleted = True
                    break
            
            if not deleted:
                logging.warning(f"Server with ID '{id}' not found")
                return
            
            # Write updated data back to file
            with open(file_path, 'w') as f:
                json.dump(file_data, f, indent=4)
                
            logging.info(f"Server with ID '{id}' deleted successfully")
        except Exception as e:
            logging.error(f"Error deleting server from storage: {e}")
            raise
