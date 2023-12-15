from abc import ABC, abstractmethod

from nodes import NodeBase

class ProcessorBase(ABC):

    @property
    @staticmethod
    @abstractmethod
    def consumed_nodetypes() -> list[type(NodeBase)]:
        pass

    def __init__(self, node: NodeBase) -> None:
        super().__init__()
        self.node = node

    @abstractmethod
    def process(self) -> list[NodeBase]:
        pass