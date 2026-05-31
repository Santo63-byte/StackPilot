from pydantic import BaseModel
from typing import Any, List, Optional


class AddServerRequest(BaseModel):
    """Request model for adding a new server."""
    server_id: str
    server_name: str
    root_path: str
    runnable_command: str
    notes: Optional[str] = None # not using as of now
    clone_from : Optional[str] = None # used for cloning server details from an existing server (except server_id and server_name)
    
class BatchStartRequest(BaseModel):
    server_ids: List[str] 
    delay_seconds: Optional[int] = 2  

class CreateSessionRequest(BaseModel):
    session_name: str

class UpdateSessionRequest(BaseModel):
    session_name: str
    
class SessionInfoHolder(BaseModel):
    session_id: str
    server_lists: List[Any]
    
class ServerInterActionRequest(BaseModel):
    action: str
    source_session_info: SessionInfoHolder
    target_session_info: SessionInfoHolder

class ProxySettingsRequest(BaseModel):
    root_path: Optional[str] = None

class BasicSettingsRequest(BaseModel):
    refresh_interval: Optional[int] = None
    terminal: Optional[str] = None

class UpdateAppSettingsRequest(BaseModel):
    basic_settings: BasicSettingsRequest
    advanced_settings: dict = {}
