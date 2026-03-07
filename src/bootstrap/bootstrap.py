from pathlib import Path
from fastapi.staticfiles import StaticFiles
from view.apirouter import router
from bootstrap.managers import ConfigManager, FileManager
from fastapi import FastAPI

# Bootstrap class to initialize application components

class Bootstrap:
    def __init__(self,app:FastAPI, config):
        self._config_manager = ConfigManager(config)
        self._config = config
        self.app = app
        self._context = {}
        # Additional dependancies can be initialized here in future
    
    def __call__(self):
        """Main method to bootstrap the application."""
        self.initialize()
        self.append_context_to_config()
        
        
    def append_context_to_config(self):
        """Append context to the configuration for global access."""
        self._config.context = self._context
        
    def set_context(self, key: str, value) -> None:
        """Set a context value."""
        self._context[key] = value
        
    def create_context(self) -> dict:
        """Get the entire context dictionary."""
        self.set_context("app", self.app)
        self.set_context("app_info", self._config.app_info)
        self.set_context("datasources", {})  # Add this line
        
    def _do_file_setup(self) -> None:
        """Setup necessary files and directories."""
        self._file_manager = FileManager(self._context, self._config)
        self._file_manager.setup_files()
        
    def add_routers(self, app: FastAPI) -> None:
        """Add routers to the FastAPI application."""
        app.include_router(router)
    
    def mount_static_files(self, app: FastAPI) -> None:
        """Mount static files and templates directories."""
        # Get the absolute path to the interface directory
        interface_dir = Path(__file__).parent.parent / "interface"
        static_dir = interface_dir / "static"
        styles_dir = interface_dir / "styles"
        templates_dir = interface_dir / "templates"
        
        # Mount JS files
        if static_dir.exists():
            app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
        
        # Mount CSS files
        if styles_dir.exists():
            app.mount("/styles", StaticFiles(directory=str(styles_dir)), name="styles")
        
        # Mount templates
        if templates_dir.exists():
            app.mount("/templates", StaticFiles(directory=str(templates_dir)), name="templates")

    def initialize(self) -> None:
        """Initialize the application components."""
        self._config_manager.initialize()
        self.create_context()
        self._do_file_setup()
        self.add_routers(self.app)
        self.mount_static_files(self.app)
        app_name = self._config.app_info.get("app_name", "StackPilot")
    
        design = f"\n{'='*40}\n   🚀 {app_name} Started! 🚀\n{'='*40}\n"
        print(design)
      
