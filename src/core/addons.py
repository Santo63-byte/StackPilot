from custom.customaddons import CustomAddons
from core.envinspector import EnvInspector
import logging
from configs import Config

#CORE 
# Define all addons in the system here. This class can be extended to include more addons in the future.
#THis class combines both core addons and custom addons and provides a unified interface to access all addon features. The actual implementation of each addon feature is delegated to the respective manager classes (like ProxyManager for proxy related features). 
# This way, we keep the addon management modular and maintainable, allowing for easy addition of new addons in the future without cluttering this class with implementation details. 
# Each addon feature can be accessed through methods defined in this class, which internally call the appropriate methods from the respective addon managers.
class Addons:
    def __init__(self,config):
        self._addons = {}
        self._config: Config = config
        self.construct_addons()
        self._custom_addons = CustomAddons(config)
        self._env_inspector = EnvInspector()    
    
    def get_addons(self):
        return self._addons
    
    def construct_addons(self):
        """Construct and register all addons based on configuration."""
        settings = self._config.server_settings
        logging.info(f"Addons::: Constructing addons with settings: {settings}")
        core_addons = settings.get("core_addons", {})
        custom_addons = settings.get("custom_addons", {})
        for addon_name in core_addons:
            self._addons[addon_name] = core_addons[addon_name]
        for addon_name in custom_addons:
            self._addons[addon_name] = custom_addons[addon_name]
    
    # Define COre addon features below as methods and call impl from respective addon manager classes (dont implement logic here, just call the respective manager class methods here)

    #FOr GIT brnach detection
    def get_git_branch_name(self, repo_path: str = None):
        """Get the current Git branch name for a given repository path."""
        return self._env_inspector.get_git_branch_name(repo_path)
    
    def is_file_path_valid(self, server:dict):
        #checking file path is there in system or not and if not appending warning to server dict
        file_path_present = self._env_inspector.is_file_path_valid(server.get('root_path', ''))
        server['warnings'].append({'file_path_present': file_path_present})
        
    def append_warnings(self, server:dict):
        # This method can be used to append any warnings or informational messages to the server dict based on certain conditions. 
        server['warnings'] = []
        self.is_file_path_valid(server)
        
        
