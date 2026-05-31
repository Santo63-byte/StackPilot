
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
from pathlib import Path
from interface.routers.app_manager import AppManager
from interface.routers.server_manager import ServerManager
from interface.routers.session_manager import SessionManager
from core.server_processor import ProcessRegistry
from interface.routers.console_manager import ConsoleManager
from view.modals.server import Server
import view.modals.basemodals as basemodals
from configs import Config
import asyncio
import logging
import json

router = APIRouter(prefix="/sp")

app_manager = AppManager()
sm = ServerManager()
session_manager = SessionManager()
console_manager = ConsoleManager()

@router.get("/")
def serve_devdock_html():
    """Serve the main DevDock HTML page."""
    if Config().context.get("backend_only", False):
        return JSONResponse(status_code=410, content={"message": "UI not available in backend-only mode"})
    logging.info("Serving main DevDock HTML page")
    template_dir = Path(__file__).parent.parent / "interface" / "templates"
    html_file = template_dir / "stackpilotview.html"
    return FileResponse(str(html_file), media_type="text/html")

# --- Server Management Endpoints ---
@router.get("/list/{session_id}/servers")
def list_servers(session_id: str):
    """List all servers."""
    logging.info("Fetching list of all servers")
    return sm.list_servers(session_id)

@router.post("/servers/{session_id}/add")
def add_server(session_id: str, request: basemodals.AddServerRequest):
    
    """Add a new server."""
    logging.info(f"Received Add Server Request: {request}")
    server = Server(
        server_id=request.server_id,
        server_name=request.server_name,
        root_path=request.root_path,
        runnable_command=request.runnable_command,
        git_branch="unknown"
    )
    result = sm.add_server(server, session_id)
    if result:
        logging.info(f"Server '{request.server_name}' added successfully")
        return {"status": 200, "message": "Server added successfully"}
    logging.error(f"Failed to add server '{request.server_name}'")
    return {"status": 500, "message": "Failed to add server"}

@router.post("/servers/batch/start")
def batch_start_servers(batches: basemodals.BatchStartRequest):
    """Start multiple servers by their IDs."""
    return sm.batch_start_servers(batches)

@router.post("/servers/{session_id}/{id}/start")
def start_server(session_id: str, id: str):
    """Start a server by ID."""
    logging.info(f"Starting server with ID: {id}")
    return sm.start_server(id,session_id)
    
@router.post("/servers/{session_id}/{id}/stop")
def stop_server(session_id: str, id: str):
    """Stop a server by ID."""
    logging.info(f"Stopping server with ID: {id}")
    return sm.stop_server(id)

@router.post("/servers/checkrunningstatus/{server_id}")
def check_running_status(server_id: str):
    """Check if a server is currently running by ID."""
    logging.info(f"Checking running status for server with ID: {server_id}")
    # return sm.check_running_status(server_id)

@router.put("/servers/{session_id}/edit")
def edit_server(session_id: str, request: basemodals.AddServerRequest):
    """Edit a server by ID."""
    logging.info(f"Received Edit Server Request: {request}")
    server = Server(
        server_id=request.server_id,
        server_name=request.server_name,
        root_path=request.root_path,
        runnable_command=request.runnable_command,
        git_branch="unknown"
    )
    result = sm.update_server(server, session_id)
    if result:
        logging.info(f"Server '{request.server_name}' updated successfully")
        return {"status": 200, "message": "Server updated successfully"}
    logging.error(f"Failed to update server '{request.server_name}'")
    return {"status": 500, "message": "Failed to update server"}

@router.delete("/servers/delete")
def delete_server(delete_info: basemodals.SessionInfoHolder):
    """Delete a server by ID."""
    res = sm.delete_servers(delete_info.server_lists, delete_info.session_id)
    if res:
        logging.info(f"Servers with IDs '{delete_info.server_lists}' deleted successfully from session '{delete_info.session_id}'")
        return {"status": 200, "message": "Server(s) deleted successfully"}
    logging.error(f"Failed to delete servers with IDs '{delete_info.server_lists}' from session '{delete_info.session_id}'")
    return {"status": 500, "message": "Failed to delete server(s)"}

@router.post("/servers/move")
def move_server(request: basemodals.ServerInterActionRequest):
    res = sm.move_servers(
        movable_server_ids=request.source_session_info.server_lists,
        source_session_id=request.source_session_info.session_id,
        target_session_id=request.target_session_info.session_id
    )
    if res:
        logging.info(f" Successfully moved successfully from session '{request.source_session_info.session_id}' to session '{request.target_session_info.session_id}'")
        return {"status": 200, "message": "Server moved successfully"}
    logging.error(f"Failed to move server  from session '{request.source_session_info.session_id}' to session '{request.target_session_info.session_id}'")
    return {"status": 500, "message": "Failed to move server"}

@router.post("/servers/copy")
def copy_server(request: basemodals.ServerInterActionRequest):
    res = sm.copy_servers(
        copyable_server_ids=request.source_session_info.server_lists,
        source_session_id=request.source_session_info.session_id,
        target_session_id=request.target_session_info.session_id
    )
    if res:
        logging.info(f"Server(s) successfully copied from session '{request.source_session_info.session_id}' to session '{request.target_session_info.session_id}'")
        return {"status": 200, "message": "Server copied successfully"}
    logging.error(f"Failed to copy server(s) from session '{request.source_session_info.session_id}' to session '{request.target_session_info.session_id}'")
    return {"status": 500, "message": "Failed to copy server(s)"}

# --- App Render Attributes & Utils Endpoint ---
@router.get("/app/render-attributes")
def get_app_render_attributes():
    logging.info("Fetching app render attributes")
    return{
        "render_attributes": app_manager.get_app_render_attributes()
    }

@router.get("/app/settings")
def get_app_settings():
    logging.info("Fetching app settings")
    return {
        "app_settings": app_manager.get_app_settings()
    }

@router.post("/app/settings/update")
def update_app_settings(new_settings: basemodals.UpdateAppSettingsRequest):
    logging.info(f"Received request to update app settings: {new_settings}")
    app_manager.update_app_settings(new_settings.model_dump())
    return {"status": 200, "message": "App settings updated successfully"}


    
# --- Config Download / Upload Endpoints ---
@router.get("/config/download")
def download_server_config():
    """Download the server list configuration as a JSON file."""
    logging.info("Received request to download server config")
    file_path = app_manager.download_server_config()
    logging.error(f"SPServerManagerDebug::: Server config file path for download: {file_path}")
    if not file_path or not Path(file_path).exists():
        logging.error("Server config file not found for download")
        return JSONResponse(status_code=404, content={"message": "Server config file not found"})
    logging.info(f"Serving server config file: {file_path}")
    try:
        file =  FileResponse(
            path=file_path,
            media_type="application/json",
            filename="serverlist.json",
            headers={"Content-Disposition": "attachment; filename=serverlist.json"}
        )
        logging.info(f"Server config file response prepared successfully for file: {file_path}")
        return file
    except Exception as e:
        logging.error(f"Error preparing server config file response: {e}")
        return JSONResponse(status_code=500, content={"message": "Error preparing server config file for download"})

@router.post("/config/upload")
async def upload_server_config(file: UploadFile):
    """Upload and override the server list configuration JSON file."""
    logging.info("Received request to upload server config")
    try:
        content = await file.read()
        new_config = json.loads(content)
    except json.JSONDecodeError as e:
        logging.error(f"Invalid JSON file uploaded: {e}")
        return JSONResponse(status_code=400, content={"message": "Invalid JSON file"})
    result = app_manager.upload_server_config(new_config)
    if result:
        logging.info("Server configontext uploaded successfully")
        return {"status": 200, "message": "Server config uploaded successfully"}
    logging.error("Failed to upload server config")
    return JSONResponse(status_code=500, content={"message": "Failed to upload server config"})

@router.post("/config/native-upload")
def native_browse_and_upload_server_config():
    """Desktop-mode: open native file dialog, read JSON, and upload config directly."""
    logging.info("Received native upload request (desktop mode)")
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        file_path = filedialog.askopenfilename(
            title="Select Server Config (JSON)",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        root.destroy()
        if not file_path:
            logging.info("No file selected in native upload dialog")
            return {"status": 204, "cancelled": True, "message": "No file selected"}
        with open(file_path, 'r', encoding='utf-8') as f:
            new_config = json.load(f)
        result = app_manager.upload_server_config(new_config)
        if result:
            logging.info("Server config uploaded successfully via native dialog")
            return {"status": 200, "message": "Server config uploaded successfully"}
        logging.error("Failed to upload server config via native dialog")
        return JSONResponse(status_code=500, content={"message": "Failed to upload server config"})
    except json.JSONDecodeError as e:
        logging.error(f"Invalid JSON in native upload: {e}")
        return JSONResponse(status_code=400, content={"message": f"Invalid JSON file: {e}"})
    except Exception as e:
        logging.error(f"Error in native upload: {e}")
        return JSONResponse(status_code=500, content={"message": str(e)})


@router.get("/browse-folder")
def browse_folder():
    """Open a native folder browser dialog and return the selected path."""
    if Config().context.get("backend_only", False):
        return JSONResponse(status_code=410, content={"message": "Native folder browser not available in backend-only mode. Use client-side file picker."})
    logging.info("Folder browser dialog opened")
    try:
        import tkinter as tk
        from tkinter import filedialog
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
# --- Session Endpoints ---
@router.get("/sessions")
def get_sessions():
    """Get all sessions sorted by creation date (newest first)."""
    logging.info("Fetching all sessions")
    sessions = session_manager.get_sessions()
    return {"sessions": sessions}

@router.post("/sessions")
def create_session(request: basemodals.CreateSessionRequest):
    """Create a new session."""
    logging.info(f"Creating session: {request.session_name}")
    result = session_manager.create_session(request.session_name)
    if result.get("success"):
        return {"status": 200, "message": result.get("message")}
    return {"status": 400, "message": result.get("message")}

@router.put("/sessions/{session_id}")
def update_session(session_id: str, request: basemodals.UpdateSessionRequest):
    """Update the name of a session by ID."""
    logging.info(f"Updating session ID '{session_id}' to name '{request.session_name}'")
    result = session_manager.update_session(session_id, {"session_name": request.session_name})
    if result:
        return {"status": 200, "message": f"Session '{session_id}' updated successfully"}
    return {"status": 400, "message": f"Failed to update session '{session_id}'"}

@router.delete("/sessions/{session_id}")
def delete_session(session_id: str):
    """Delete a session by ID."""
    logging.info(f"Deleting session with ID: {session_id}")
    result = session_manager.delete_session(session_id)
    if result:
        return {"status": 200, "message": f"Session '{session_id}' deleted successfully"}
    return {"status": 500, "message": f"Failed to delete session '{session_id}'"}

#For Console Drawer 
# --- Process Log Streaming (WebSocket) ---

@router.post("/console/killport/{port}")
def kill_port(port: int):
    """Kill any process using the specified port."""
    logging.info(f"Attempting to kill any process using port: {port}")
    result = console_manager.kill_port(port)
    if result.get("status") == 200:
        logging.info(f"Successfully killed process on port {port}")
        return {"status": 200, "message": result.get("message")}
    logging.error(f"Failed to kill process on port {port}: {result.get('message')}")
    return {"status": 500, "message": result.get("message")}

@router.post("/console/openadavancedterminal")
def open_terminal(path: str = ""):
    """Open a new terminal at the specified path."""
    logging.info(f"Opening terminal at path: {path}")
    result = console_manager.open_advanced_terminal(path)
    if result.get("status") == 200:
        logging.info("Terminal opened successfully")
        return {"status": 200, "message": result.get("message")}


#Dummy implementation for now, will be moved to console manager later
@router.websocket("/console/{server_name}/logs")
async def stream_server_logs(websocket: WebSocket, server_name: str):
    """Stream live stdout logs for a running server process identified by server_name."""
    await websocket.accept()
    logging.info(f"WebSocket log stream opened for server: '{server_name}'")

    process_registry = ProcessRegistry()
    process = process_registry.registered_processes.get(server_name)

    if process is None:
        await websocket.send_text(f"[ERROR] No registered process found for '{server_name}'")
        await websocket.close()
        return

    if process.stdout is None:
        await websocket.send_text(
            f"[ERROR] Process '{server_name}' was started without stdout capture "
            "(e.g. Windows_Terminal mode). Log streaming is not available."
        )
        await websocket.close()
        return

    loop = asyncio.get_event_loop()
    try:
        while True:
            # readline() is blocking — run it in a thread-pool executor to avoid blocking the event loop
            line: str = await loop.run_in_executor(None, process.stdout.readline)
            if not line:
                await websocket.send_text("[PROCESS ENDED]")
                logging.info(f"Process '{server_name}' stdout closed (EOF)")
                break
            await websocket.send_text(line.rstrip("\n"))
    except WebSocketDisconnect:
        logging.info(f"WebSocket client disconnected from log stream: '{server_name}'")
    except Exception as e:
        logging.error(f"WebSocket log stream error for '{server_name}': {e}")
    finally:
        await websocket.close()


# Notes Drawer Endpoints (To be moved to a separate router file in the future)

# def get_notes():
#     """Get all notes."""
#     logging.info("Fetching all notes")
#     # Placeholder implementation - replace with actual note retrieval logic
#     return {"notes": []}

# def create_note(request: basemodals.CreateNoteRequest):
#     """Create a new note."""
#     logging.info(f"Creating note with title: {request.title}")
#     # Placeholder implementation - replace with actual note creation logic
#     return {"status": 200, "message": "Note created successfully"}
