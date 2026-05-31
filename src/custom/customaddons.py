from custom.proxy_manager import ProxyManager


class CustomAddons:
    
    def __init__(self,config):
        # Initialize all custom addon managers here
        self._proxymanager = ProxyManager(config)
    
    # Define all custom addon features as methods here that utilize the respective managers
    def set_proxy_environment(self, env_key: str):
        """Set the active proxy environment."""
        return self._proxymanager.set_active_environment(env_key)
    
    def get_available_proxy_environments(self):
        """Get list of available proxy environments."""
        return self._proxymanager.get_available_environments()
    
    def get_current_proxy_environment(self) :
        """Get the currently active proxy environment."""
        # This method can be implemented to read the current environment from the proxy config file if needed
        return self._proxymanager.get_current_environment()
    
    def start_proxy(self):
        """Start the proxy server if proxy settings are enabled."""
        return self._proxymanager.start_proxy_server()
    
    def is_proxy_running(self):        
        """Check if the proxy server process is currently running."""
        return self._proxymanager.is_proxy_running()
    
    def get_proxy_root_path(self):
        """Get the root path for the proxy configuration file."""
        return self._proxymanager.get_proxy_root_path(folder_path_only=True)
    
    def save_proxy_config(self, settings:dict):
        """Save the proxy configuration for a specific environment."""
        return self._proxymanager.save_proxy_config(settings=settings)
