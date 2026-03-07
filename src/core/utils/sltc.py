import threading

# Singleton Metacls
class SingletonMeta(type):
    """
    A metaclass for creating singleton classes(thread safe)
    """
    _lock=threading.RLock()
    __instances__ = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls.__instances__:
            with cls._lock:
                if cls not in cls.__instances__:
                    cls.__instances__[cls] = super().__call__(*args, **kwargs)
        return cls.__instances__[cls]
    
# SLTC(inherit this to make ur object singleton instance)
class SLTC(metaclass=SingletonMeta):
    """
    Parent class for converting the inherited child to have singleton instance.
    """
    pass
