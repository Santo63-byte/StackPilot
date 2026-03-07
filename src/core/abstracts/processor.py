
from abc import ABC, abstractmethod


# @abstract class
class Processor(ABC):
    @abstractmethod
    def pre_process(self, data):
        """Pre-process raw data before main processing."""
        pass
    
    @abstractmethod
    def start(self):
        pass
    
    @abstractmethod
    def stop(self):
        pass
    
    @abstractmethod
    def restart(self):
        pass
