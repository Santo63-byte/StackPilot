from typing import Optional

class Server:
    def __init__(
        self,
        server_id: str,
        server_name: str,
        root_path: str,
        runnable_command: str,
        port_no: Optional[int] = None,
        pid_status: int = 0,
        git_branch: str = "unknown"
    ):
        self.server_id = server_id
        self.server_name = server_name
        self.root_path = root_path
        self.runnable_command = runnable_command
        self.port_no = port_no
        self.pid_status = pid_status
        self.git_branch = git_branch

    def to_dict(self) -> dict:
        """Convert server object to dictionary."""
        return {
            "server_id": self.server_id,
            "server_name": self.server_name,
            "root_path": self.root_path,
            "runnable_command": self.runnable_command,
            "port_no": self.port_no,
            "pid_status": self.pid_status,
            "git_branch": self.git_branch
        }
