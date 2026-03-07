from pydantic import BaseModel
from typing import Optional


class AddServerRequest(BaseModel):
    """Request model for adding a new server."""
    server_id: str
    server_name: str
    root_path: str
    runnable_command: str
    port_no: Optional[int] = None
    notes: Optional[str] = None 
