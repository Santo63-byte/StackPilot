
from configs import Config
from core.utils import SLTC
from fastapi import FastAPI
from bootstrap import Bootstrap

#########################################################################################
# The main application class that initializes FastAPI and loads configurations using the Bootstrap class.
# Intentionally made to singleton instance as it is intended to be a desktop application with strict one  instance...
class Application(SLTC):
    # Application class that initializes  and loads configurations
    def __init__(self, services_only=False):
        self.app:FastAPI = FastAPI()
        self._config = Config()
        Bootstrap(self.app, self._config,services_only)()
##########################################################################################
