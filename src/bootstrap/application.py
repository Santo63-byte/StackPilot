
from configs import Config
from core.utils import SLTC
from fastapi import FastAPI
from bootstrap import Bootstrap

#########################################################################################
class Application(SLTC):
    # Singleton Application class that initializes FastAPI and loads configurations
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        self.app:FastAPI = FastAPI()
        self._config = Config()
        Bootstrap(self.app, self._config)()
##########################################################################################
