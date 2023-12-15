import sys, inspect
from config import KeyscoreConfig
from nodes import NodeBase
from processor import ProcessorBase
from processors import *

class KeyscoreSession():

    _nodeclass_map = {}
    _processor_consume_map = {}

    def __init__(self, start_nodes: list[NodeBase]) -> None:
        self.start_nodes = start_nodes.copy()
        self.processed = []
        self.queued = start_nodes.copy()

    @staticmethod
    def from_ksd(path: str):
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
        return KeyscoreSession(nodes)
    
    def process(self):
        while len(self.queued) > 0:
            process_node = self.queued.pop(0)
            if process_node.get_depth() >= KeyscoreConfig.get("depth"):
                self.processed.append(process_node)
                continue

            processors = KeyscoreSession._processor_consume_map[type(process_node)]
            for pclass in processors:
                processor: ProcessorBase = pclass(process_node)
                new_nodes = processor.process() or []
                for new_node in new_nodes:
                    if self.should_add_node(new_node) and not process_node.equals(new_node):
                        new_node.parent = process_node
                        self.queued.append(new_node)
            self.processed.append(process_node)
        return self.processed
    
    def should_add_node(self, node: NodeBase):
        for processed in self.processed:
            if node.equals(processed):
                return False
        for queued in self.queued:
            if node.equals(queued):
                return False
        return True



modules = list(sys.modules.values())
for module in modules:
    try:
        all_node_members = inspect.getmembers(module)
        for ncl in all_node_members:
            if not inspect.isclass(ncl[1]) or ncl[1] is NodeBase:
                continue
            if issubclass(ncl[1], NodeBase):
                KeyscoreSession._nodeclass_map[ncl[0]] = ncl[1]
    except:
        pass

all_processor_members = inspect.getmembers(sys.modules["processors"])
for pm in all_processor_members:
    if not inspect.ismodule(pm[1]):
        continue
    all_pmodule_members = inspect.getmembers(pm[1])
    for pcl in all_pmodule_members:
        if not inspect.isclass(pcl[1]) or pcl[1] is ProcessorBase:
            continue
        if issubclass(pcl[1], ProcessorBase):
            for consumed in pcl[1].consumed_nodetypes:
                if consumed in KeyscoreSession._processor_consume_map:
                    KeyscoreSession._processor_consume_map[consumed].append(pcl[1])
                else:
                    KeyscoreSession._processor_consume_map[consumed] = [pcl[1]]
