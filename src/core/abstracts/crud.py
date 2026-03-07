
from abc import ABC, abstractmethod

class CRUD(ABC):
    
    @abstractmethod
    def create(self, data):
        pass

    @abstractmethod
    def readAll(self, id: str):
        pass

    @abstractmethod
    def update(self, id: str, data) -> None:
        pass

    @abstractmethod
    def delete(self, id: str) -> None:
        pass
