from config import KeyscoreConfig
from nodes import NodeBase
from processor import ProcessorBase
from processors import *
from util.module_util import get_nodeclass_map, get_processor_consume_map
from loguru import logger

class KeyscoreSession():

    _nodeclass_map = get_nodeclass_map()
    _processor_consume_map = get_processor_consume_map()

    def __init__(self, start_nodes: list[NodeBase]) -> None:
        self.start_nodes = start_nodes.copy()
        self.processed = []
        self.queued = start_nodes.copy()

    @staticmethod
    def from_ksd(path: str):
        """Creates a new KeyscoreSession instance using input data from a provided KSD file."""
        nodes = []
        with open(path, "r") as f:
            lines = f.readlines()
            lines: list[str] = list(map(lambda line: line.strip(), lines))
            for line in lines:
                nodetype = line.split(":")[0]
                nodeargs = line[line.index(":") + 1:].replace("\\:", "__{COLON_PLACEHOLDER}__").split(":")
                nodeargs = list(map(lambda line: line.replace("__{COLON_PLACEHOLDER}__", ":"), nodeargs))

                if nodetype not in KeyscoreSession._nodeclass_map:
                    raise Exception(f"Cannot parse node of unknown type {nodetype}")
                nodes.append(KeyscoreSession._nodeclass_map[nodetype](*nodeargs))
        logger.info(f"Initialized Keyscore Session with {len(nodes)} node{'s' if len(nodes) > 1 else ''}.")
        return KeyscoreSession(nodes)
    
    def process(self):
        """Processes the input data the session was initialized with and returns a list of all resulting nodes."""
        processor_whitelist = KeyscoreConfig.get("only_processors")
        while len(self.queued) > 0:
            process_node = self.queued.pop(0)
            if process_node.get_depth() >= KeyscoreConfig.get("depth"):
                self.processed.append(process_node)
                continue

            if type(process_node) not in KeyscoreSession._processor_consume_map:
                self.processed.append(process_node)
                continue

            processors = KeyscoreSession._processor_consume_map[type(process_node)]
            for pclass in processors:
                # Handling for --only-processors argument
                if len(processor_whitelist) > 0 and pclass.__name__ not in processor_whitelist:
                    continue

                processor: ProcessorBase = pclass(process_node)
                logger.info(f"Processing {process_node.__class__.__name__} {process_node} with {processor.__class__.__name__}")
                new_nodes = processor.process() or []
                for new_node in new_nodes:
                    if self.should_add_node(new_node) and not process_node.equals(new_node):
                        if new_node.parent is None:
                            new_node.parent = process_node
                        logger.info(f"Found {new_node._type_display_name}: {new_node}")
                        self.queued.append(new_node)
            self.processed.append(process_node)
        return self.processed
    
    def should_add_node(self, node: NodeBase):
        """Returns False if the provided node is already known within the context of the session, True otherwise"""
        for processed in self.processed:
            if node.equals(processed):
                return False
        for queued in self.queued:
            if node.equals(queued):
                return False
        return True
