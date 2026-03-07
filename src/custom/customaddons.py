from custom.proxy_manager import ProxyManager

class CustomAddons:
    
    def __init__(self,config):
        self._proxymanager = ProxyManager(config)
    
    # Define all custom addon features as methods here that utilize the respective addon managers
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
