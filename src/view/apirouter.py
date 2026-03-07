
from fastapi import APIRouter
from fastapi.responses import FileResponse
from pathlib import Path
from core.server_manager import ServerManager
from view.modals.server import Server
from view.modals.basemodals import AddServerRequest
import tkinter as tk
from tkinter import filedialog
import logging

router = APIRouter(prefix="/sp")
sm = ServerManager()

@router.get("/")
def serve_devdock_html():
    """Serve the main DevDock HTML page."""
    logging.info("Serving main DevDock HTML page")
    template_dir = Path(__file__).parent.parent / "interface" / "templates"
    html_file = template_dir / "devdockview.html"
    return FileResponse(str(html_file), media_type="text/html")

@router.get("/list/servers")
def list_servers():
    """List all servers."""
    logging.info("Fetching list of all servers")
    return sm.list_servers()

@router.post("/servers/add")
def add_server(request: AddServerRequest):
    """Add a new server."""
    logging.info(f"Received Add Server Request: {request}")
    server = Server(
        server_id=request.server_id,
        server_name=request.server_name,
        root_path=request.root_path,
        runnable_command=request.runnable_command,
        port_no=request.port_no,
        pid_status=0,
        git_branch="unknown"
    )
    result = sm.add_server(server)
    if result:
        logging.info(f"Server '{request.server_name}' added successfully")
        return {"status": 200, "message": "Server added successfully"}
    logging.error(f"Failed to add server '{request.server_name}'")
    return {"status": 500, "message": "Failed to add server"}

@router.post("/servers/{id}/start")
def start_server(id: str):
    """Start a server by ID."""
    logging.info(f"Starting server with ID: {id}")
    return sm.start_server(id)

@router.post("/servers/{id}/stop")
def stop_server(id: str):
    """Stop a server by ID."""
    logging.info(f"Stopping server with ID: {id}")
    return sm.stop_server(id)

@router.get("/browse-folder")
def browse_folder():
    """Open a native folder browser dialog and return the selected path."""
    logging.info("Folder browser dialog opened")
    try:
        root = tk.Tk()
        root.withdraw()  
        root.attributes('-topmost', True) 
        folder_path = filedialog.askdirectory(
            title="Select Server Directory",
            parent=root
        )
        root.destroy()  
        if folder_path:
            logging.info(f"Folder selected: {folder_path}")
            return {"success": True, "path": folder_path}
        else:
            logging.info("No folder selected by user")
            return {"success": False, "path": None, "message": "No folder selected"}
    except Exception as e:
        logging.error(f"Error in folder browser: {e}")
        return {"success": False, "path": None, "message": str(e)}

@router.put("/servers/edit")
def edit_server(request: AddServerRequest):
    """Edit a server by ID."""
    logging.info(f"Received Edit Server Request: {request}")
    server = Server(
        server_id=request.server_id,
        server_name=request.server_name,
        root_path=request.root_path,
        runnable_command=request.runnable_command,
        port_no=request.port_no,
        pid_status=0,
        git_branch="unknown"
    )
    result = sm.update_server(server)
    if result:
        logging.info(f"Server '{request.server_name}' updated successfully")
        return {"status": 200, "message": "Server updated successfully"}
    logging.error(f"Failed to update server '{request.server_name}'")
    return {"status": 500, "message": "Failed to update server"}

@router.delete("/servers/{id}")
def delete_server(id: str):
    """Delete a server by ID."""
    return sm.remove_server(id)

@router.get("/app/render-attributes")
def get_app_render_attributes():
    logging.info("Fetching app render attributes")
    return{
        "render_attributes": sm.get_app_render_attributes()
    }

@router.get("/proxy/environments/lookup")
def get_available_proxy_envs():
    """Get list of available proxy environments."""
    logging.info("Fetching available proxy environments")
    return {
        "environments": sm.get_available_proxy_envs()
    }
    
@router.post("/proxy/environments/set")
def set_proxy_environment(env: str):
    """Set the active proxy environment."""
    logging.info(f"Setting proxy environment to: {env}")
    result = sm.set_proxy(env)
    if result:
        logging.info(f"Proxy environment successfully set to '{env}'")
        return {"status": 200, "message": f"Proxy environment set to '{env}' successfully"}
    logging.error(f"Failed to set proxy environment to '{env}'")
    return {"status": 500, "message": f"Failed to set proxy environment to '{env}'"}
