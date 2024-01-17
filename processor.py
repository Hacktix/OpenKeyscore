from abc import ABC, abstractmethod

from nodes import NodeBase

class ProcessorBase(ABC):

    @property
    @staticmethod
    @abstractmethod
    def consumed_nodetypes() -> list[type(NodeBase)]:
        """List of types of Nodes which, when it's their turn to be processed, should be sent to this processor."""
        pass

    def __init__(self, node: NodeBase) -> None:
        super().__init__()
        self.node = node

    @abstractmethod
    def process(self) -> list[NodeBase]:
        """Main function of the Processor, where input nodes are used to generate new nodes to add to the results."""
        pass

class SearchProcessorBase(ABC):
    url_regexes = []
    """List of Regexes that, when matching with a found URL, signifies that this processor should be used to process it."""

    @abstractmethod
    def get_nodes_from_search_result(url: str) -> list[NodeBase]:
        """Function which returns a list of new nodes to add to results based on a given URL which was found through the use of a search engine."""
        pass