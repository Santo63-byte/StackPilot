from storage import SessionStorage
from configs import Config
from datetime import datetime
import uuid
import logging

class SessionManager():
    
    def __init__(self):
        self.storage = SessionStorage()
        self._config = Config()

    def validate_session(self, session_name: str):
        """Validate session name."""
        if not session_name or session_name.strip() == "":
            return "Session name is mandatory"
        sessions = self.storage.readAll()
        if any(s.get("session_name") == session_name for s in sessions):
            return "Session name must be unique. A session with this name already exists."
        return 'valid'
    
    def _generate_id(self) :
        """Generate a unique 10-character session ID."""
        return uuid.uuid4().hex[:10]
    
    def create_session(self, session_name: str):
        """Create a new session with the given name."""
        message = self.validate_session(session_name)
        if message != 'valid':
            logging.error(f"Error creating session: {message}")
            return {
                "success": False,
                "message": message
            }
        session = {
            "session_name": session_name,
            "session_id": self._generate_id(),
            "date_created": datetime.now().strftime("%d%m%Y%H%M%S")
        }
        try:
            self.storage.create(session)
            return {
                "success": True,
                "message": f"Session '{session_name}' created successfully with ID '{session['session_id']}'"
            }
        except Exception as e:
            logging.error(f"Error creating session: {e}")
            return {
                "success": False,
                "message": f"Error creating session: {e}"
            }
        
    def get_sessions(self):
        """Get a list of all sessions sorted by creation date (newest first)."""
        try:
            sessions = self.storage.readAll()
            
            # Sort sessions by date_created in descending order (newest first)
            def parse_date(session):
                try:
                    return datetime.strptime(session.get("date_created", ""), "%d%m%Y%H%M%S")
                except ValueError:
                    return datetime.min

            sorted_sessions = sorted(sessions, key=parse_date, reverse=True)

            return [
                {"session_name": s.get("session_name"), "session_id": s.get("session_id"), "date_created": s.get("date_created")}
                for s in sorted_sessions
            ]
        except Exception as e:
            logging.error(f"Error getting sessions: {e}")
            return []
        
    def update_session(self, session_id: str, session):
        """Update the name of a session identified by session_id."""
        message = self.validate_session(session.get("session_name"))
        if message != 'valid':
            logging.error(f"Error creating session: {message}")
            return {
                "success": False,
                "message": message
            }
        try:
            return self.storage.update(session_id, session)
        except Exception as e:
            logging.error(f"Error updating session: {e}")
            return False
        
    def delete_session(self, session_id: str):
        """Delete a session by its ID."""
        try:
            self.storage.delete(session_id)
            return True
        except Exception as e:
            logging.error(f"Error deleting session: {e}")
            return False
