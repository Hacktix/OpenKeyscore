from abc import ABC
from typing import ClassVar

class FieldBase(ABC):
    value: ClassVar[any]
    def __init__(self, value) -> None:
        super().__init__()
        self.value = value

class StringField(FieldBase):
    value: ClassVar[str]
    def __init__(self, value: str) -> None:
        super().__init__(value)
        self.value