
from abc import ABC, abstractmethod


# @abstract class
class Processor(ABC):
    
    @abstractmethod
    def start(self):
        pass
    
    @abstractmethod
    def kill(self):
        pass
    
    @abstractmethod
    def restart(self):
        pass
