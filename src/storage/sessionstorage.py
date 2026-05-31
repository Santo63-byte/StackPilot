
from core.abstracts.crud import CRUD
from typing import override
from configs import Config
import json
import logging
from datetime import datetime

class SessionStorage(CRUD):

    def __init__(self):
        self.config = Config()

    def _get_context(self):
        """Get the app context."""
        return self.config.context

    def _get_file_path(self) -> str:
        """Get the user sessions file path from config context."""
        context = self._get_context()
        data_resources = context.get("datasources", {})
        return data_resources.get("server_list")

    @override
    def create(self, data) -> None:
        """Create a new session. data is a dict with 'session_name'."""
        file_path = self._get_file_path()

        try:
            try:
                with open(file_path, 'r') as f:
                    file_data = json.load(f)
            except FileNotFoundError:
                file_data = {"default_user": {"server_lists": []}}
            except json.JSONDecodeError:
                logging.error(f"Error decoding JSON from: {file_path}, initializing fresh.")
                file_data = {"default_user": {"server_lists": []}}

            user_key = "default_user"
            if user_key not in file_data:
                file_data[user_key] = {"server_lists": []}
            if "server_lists" not in file_data[user_key]:
                file_data[user_key]["server_lists"] = []

            new_session = {
                "session_name": data.get("session_name"),
                "session_id": data.get("session_id"),
                "date_created": data.get("date_created"),
                "servers": []
            }
            file_data[user_key]["server_lists"].append(new_session)

            with open(file_path, 'w') as f:
                json.dump(file_data, f, indent=4)

            logging.info(f"Session '{new_session['session_name']}' created successfully with ID '{new_session['session_id']}'")
        except Exception as e:
            logging.error(f"Error creating session in storage: {e}")
            raise

    @override
    def readAll(self):
        """Read all sessions, returning [{session_name, session_id, date_created}] sorted by date_created ascending."""
        file_path = self._get_file_path()
        if not file_path:
            logging.warning("No data sources found in context.")
            return []

        try:
            with open(file_path, 'r') as f:
                file_data = json.load(f)

            server_lists = file_data.get("default_user", {}).get("server_lists", [])

            def parse_date(session):
                try:
                    return datetime.strptime(session.get("date_created") or "", "%d%m%Y%H%M%S")
                except ValueError:
                    return datetime.min

            sorted_sessions = sorted(server_lists, key=parse_date)

            return [
                {
                    "session_name": s.get("session_name"),
                    "session_id": s.get("session_id"),
                    "date_created": s.get("date_created")
                }
                for s in sorted_sessions
            ]
        except FileNotFoundError:
            logging.error(f"Session file not found: {file_path}")
            return []
        except json.JSONDecodeError:
            logging.error(f"Error decoding JSON from: {file_path}")
            return []
        except Exception as e:
            logging.error(f"Error reading sessions: {e}")
            return []

    @override
    def update(self, id: str, data) -> bool:
        """Update the session_name of a session identified by session_id. data is a dict with 'session_name'."""
        file_path = self._get_file_path()

        try:
            with open(file_path, 'r') as f:
                file_data = json.load(f)

            server_lists = file_data.get("default_user", {}).get("server_lists", [])

            new_name = data.get("session_name") if isinstance(data, dict) else None
            if not new_name:
                logging.error("'session_name' is required in data for update")
                return False

            updated = False
            for session in server_lists:
                if str(session.get("session_id")) == str(id):
                    session["session_name"] = new_name
                    updated = True
                    break

            if not updated:
                logging.warning(f"Session with ID '{id}' not found")
                return False

            with open(file_path, 'w') as f:
                json.dump(file_data, f, indent=4)

            logging.info(f"Session with ID '{id}' updated to name '{new_name}'")
            return True
        except FileNotFoundError:
            logging.error(f"Session file not found: {file_path}")
            return False
        except json.JSONDecodeError:
            logging.error(f"Error decoding JSON from: {file_path}")
            return False
        except Exception as e:
            logging.error(f"Error updating session in storage: {e}")
            return False

    @override
    def delete(self, id: str) -> None:
        """Delete a session from storage by session_id."""
        file_path = self._get_file_path()

        try:
            with open(file_path, 'r') as f:
                file_data = json.load(f)

            server_lists = file_data.get("default_user", {}).get("server_lists", [])
            original_length = len(server_lists)

            file_data["default_user"]["server_lists"] = [
                s for s in server_lists if str(s.get("session_id")) != str(id)
            ]

            if len(file_data["default_user"]["server_lists"]) == original_length:
                logging.warning(f"Session with ID '{id}' not found")
                return

            with open(file_path, 'w') as f:
                json.dump(file_data, f, indent=4)

            logging.info(f"Session with ID '{id}' deleted successfully")
        except FileNotFoundError:
            logging.error(f"Session file not found: {file_path}")
            raise
        except json.JSONDecodeError:
            logging.error(f"Error decoding JSON from: {file_path}")
            raise
        except Exception as e:
            logging.error(f"Error deleting session from storage: {e}")
            raise

    
