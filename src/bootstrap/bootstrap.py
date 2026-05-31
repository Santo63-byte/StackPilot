import sys
import logging
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from view.apirouter import router
from configs import Config
from bootstrap.managers import ConfigManager, FileManager

# Bootstrap class to initialize application components
class Bootstrap:
    def __init__(self,app:FastAPI, config:Config,services_only=False):
        self._config_manager = ConfigManager(config)
        self._config = config
        self.app = app
        self.services_only = services_only
        self._context = {}
        # Additional dependancies can be initialized here in future
    
    def __call__(self):
        """Main method to bootstrap the application."""
        self.initialize()
        
    def append_context_to_config(self):
        """Append context to the configuration for global access."""
        self._config.context = self._context
        
    def set_context(self, key: str, value):
        """Set a context value."""
        self._context[key] = value
        
    def get_os_info(self):
        """Get operating system information."""
        if sys.platform.startswith("win"):
            return "windows"
        elif sys.platform.startswith("darwin"):
            return "mac"
        return sys.platform
    
    def create_context(self) :
        self.set_context("app", self.app)
        self.set_context("app_info", self._config.app_info)
        self.set_context("os", self.get_os_info())
        self.set_context("datasources", {})
        self.set_context("services_only", self.services_only) 
        self.set_context("app_settings_file_path", self._config_manager.config_file_path)
        
    def _do_file_setup(self) :
        """Setup necessary files and directories."""
        self._file_manager = FileManager(self._context, self._config)
        self._file_manager.setup_files()
        
    def register_exception_handlers(self):
        """to log all unhandled exceptions."""
        
        @self.app.middleware("http")
        async def _global_exception_middleware(request: Request, call_next):
            try:
                return await call_next(request)
            except Exception:
                logging.exception(
                    "Unhandled Exception Occurred on %s %s",
                    request.method,
                    request.url.path,
                )
                return JSONResponse(
                    status_code=500,
                    content={"detail": "Internal server error"},
                )

    def add_routers(self, app: FastAPI):
        """Add routers to the FastAPI application."""
        app.include_router(router)
    
    def mount_static_files(self, app: FastAPI):
        """Mount static files and templates directories."""
        # Get the absolute path to the interface directory
        interface_dir = Path(__file__).parent.parent / "interface"
        static_dir = interface_dir / "static"
        styles_dir = interface_dir / "styles"
        templates_dir = interface_dir / "templates"
        assets_dir = interface_dir / "assets"
        
        # Mount JS files
        if static_dir.exists():
            app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
        # Mount CSS files
        if styles_dir.exists():
            app.mount("/styles", StaticFiles(directory=str(styles_dir)), name="styles")
        # Mount templates
        if templates_dir.exists():
            app.mount("/templates", StaticFiles(directory=str(templates_dir)), name="templates")
        # Mount assets (images, etc.)
        if assets_dir.exists():
            app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    def setup_middleware(self):
        self.register_exception_handlers()
        
        
    def initialize(self):
        """Initialize the application components."""
        self._config_manager.initialize()
        self.append_context_to_config()
        self.create_context()
        self._do_file_setup()
        self.setup_middleware()
        self.add_routers(self.app)
        if not self.services_only:
            self.mount_static_files(self.app)
        app_name = self._config.app_info.get("app_name", "StackPilot")
        design = f"\n{'='*40}\n   🚀 {app_name} Started! 🚀\n{'='*40}\n"
        print(design)
      
