from abc import ABC, abstractmethod
from fields import FieldBase, StringField

class NodeBase(ABC):
    def __init__(self, parent: "NodeBase" = None) -> None:
        super().__init__()
        self.parent = parent

    def get_depth(self) -> int:
        return 0 if self.parent is None else self.parent.get_depth() + 1

    @abstractmethod
    def equals(self, other) -> bool:
        pass

    @staticmethod
    @abstractmethod
    def parse(*args):
        pass

    @abstractmethod
    def __repr__(self):
        pass

class Username(NodeBase):
    def __init__(self, username: str, parent: NodeBase = None) -> None:
        super().__init__(parent)
        self.username = StringField(username)

    def equals(self, other): return self.username.value == other.username.value if type(other) == Username else False
    def __repr__(self): return self.username.value

    @staticmethod
    def parse(*args): return Username(args[0])

class Email(NodeBase):
    def __init__(self, email: str, parent: NodeBase = None) -> None:
        super().__init__(parent)
        self.email = StringField(email)

    def equals(self, other): return self.email.value == other.email.value if type(other) == Email else False
    def __repr__(self): return self.email.value

    @staticmethod
    def parse(*args): return Email(args[0])

class Website(NodeBase):
    def __init__(self, url: str, parent: NodeBase = None) -> None:
        super().__init__(parent)
        self.url = url
        self.domain = url.split("//")[1].split("/")[0] if "//" in url else url.split("/")[0]

    def equals(self, other) -> bool: return self.domain == other.domain if type(other) == Website else False
    def __repr__(self): return self.domain

    @staticmethod
    def parse(*args): return Website(args[0])