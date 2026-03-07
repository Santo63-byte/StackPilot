
import re
from pathlib import Path
from typing import  Optional, List
import logging

class ProxyManager:
    """Manages proxy configuration for the Node.js proxy server."""
    
    def __init__(self, config):
        self._config = config
        self.proxy_settings = self._config.server_settings.get("custom_addons", {}).get("proxy_settings", {})
        self.proxy_enabled = self.proxy_settings.get("enabled", False)
        self.proxy_file_path = self.proxy_settings.get("proxy_file_path")
        self.available_envs = self.proxy_settings.get("available_envs", [])
    
    def is_enabled(self):
        """Check if proxy settings are enabled."""
        return self.proxy_enabled
    
    def get_available_environments(self) -> List[str]:
        """Get list of available environment keys from config."""
        logging.info(f"ProxyManager::: Available proxy environments from config: {self.available_envs}")
        logging.info(f"ProxyManager::: Proxy file path from config: {self.proxy_file_path}")
        if self.available_envs:
            return self.available_envs
        return []
    
    def set_active_environment(self, env_key: str):
        if not self.is_enabled():
            logging.warning("Proxy settings are not enabled")
            return False
        
        if not self.proxy_file_path or not Path(self.proxy_file_path).exists():
            logging.error(f"Proxy config file not found: {self.proxy_file_path}")
            return False
        
        available_envs = self.get_available_environments()
        if env_key not in available_envs:
            logging.error(f"Unknown environment: {env_key}. Available: {available_envs}")
            return False
        try:
            with open(self.proxy_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            pattern = r'const\s+key\s*=\s*"[^"]*"'
            new_content = re.sub(pattern, f'const key = "{env_key}"', content)
            
            with open(self.proxy_file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            logging.info(f"Proxy environment set to '{env_key}'")
            return True
        
        except Exception as e:
            logging.error(f"Error setting active environment: {e}")
            return False
    
    def get_current_environment(self) -> Optional[str]:
        """Get the currently active environment from index.js."""
        if not self.proxy_file_path or not Path(self.proxy_file_path).exists():
            return None
        
        try:
            with open(self.proxy_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            match = re.search(r'const\s+key\s*=\s*"([^"]*)"', content)
            if match:
                return match.group(1)
        
        except Exception as e:
            logging.error(f"Error getting current environment: {e}")
        
        return None
    
