
from typing import Dict, Any
from core.utils.sltc import SLTC

# Config class to hold application configurations
class Config(SLTC):
    
    def __init__(self):
        self._app_info:Dict = {}
        self._server_settings:Dict = {}
        self._user_preferences:Dict= {}
        self._context:Dict = {}
    
    @property
    def app_info(self) -> Dict[str, Any]:
        return self._app_info
    
    @app_info.setter
    def app_info(self, info: Dict[str, Any]) -> None:
        self._app_info = info
        
    @property
    def server_settings(self) -> Dict[str, Any]:
        return self._server_settings
    
    @server_settings.setter
    def server_settings(self, settings: Dict[str, Any]) -> None:
        self._server_settings = settings
    
    @property
    def user_preferences(self) -> Dict[str, Any]:
        return self._user_preferences
    
    @user_preferences.setter
    def user_preferences(self, preferences: Dict[str, Any]) -> None:
        self._user_preferences = preferences
    
    @property
    def context(self) -> Dict[str, Any]:
        return self._context
    
    @context.setter
    def context(self, context: Dict[str, Any]) -> None:
        self._context = context
