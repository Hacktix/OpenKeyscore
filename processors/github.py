from nodes import NodeBase, Username
from processor import ProcessorBase

class GithubProcessor(ProcessorBase):

    consumed_nodetypes = [Username]

    def process(self) -> list[NodeBase]:
        return [] # TODO: Actually implement this