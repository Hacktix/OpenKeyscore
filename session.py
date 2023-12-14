import sys, inspect
from nodes import NodeBase

class KeyscoreSession():

    _nodeclass_map = {}

    def __init__(self, start_nodes: list[NodeBase]) -> None:
        self._start_nodes = start_nodes

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
                
all_node_members = inspect.getmembers(sys.modules["nodes"])
for ncl in all_node_members:
    if not inspect.isclass(ncl[1]) or ncl[1] is NodeBase:
        continue
    if issubclass(ncl[1], NodeBase):
        KeyscoreSession._nodeclass_map[ncl[0]] = ncl[1]