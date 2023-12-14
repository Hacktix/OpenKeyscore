from abc import ABC, abstractmethod
from fields import FieldBase

class NodeBase(ABC):
    def __init__(self, parent: "NodeBase" = None) -> None:
        super().__init__()
        self.parent = parent

    def get_depth(self) -> int:
        return 0 if self.parent is None else self.parent.get_depth() + 1

    @abstractmethod
    def get_fields(self) -> dict[str, FieldBase]:
        pass

    @abstractmethod
    def equals(self, other) -> bool:
        pass

    @abstractmethod
    def parse(*args):
        pass

    @abstractmethod
    def __repr__(self):
        pass
