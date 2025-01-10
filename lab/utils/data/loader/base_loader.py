from abc import abstractmethod
from typing import Generic, TypeVar

from ..base_pipe import PipelineStep

T = TypeVar("T")


class BaseLoader(PipelineStep, Generic[T]):
    @abstractmethod
    def execute(self, inputs: T) -> T:
        raise NotImplementedError
