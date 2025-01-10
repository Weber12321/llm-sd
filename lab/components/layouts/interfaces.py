from abc import ABC, abstractmethod


class Layout(ABC):
    
    @abstractmethod
    def __call__(self, *args, **kwargs):
        raise NotImplementedError
