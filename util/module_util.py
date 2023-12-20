import sys
import inspect
import re

from nodes import NodeBase
from processor import ProcessorBase, SearchProcessorBase

def get_nodeclass_map():
    nodeclass_map = {}
    modules = list(sys.modules.values())
    for module in modules:
        try:
            all_node_members = inspect.getmembers(module)
            for ncl in all_node_members:
                if not inspect.isclass(ncl[1]) or ncl[1] is NodeBase:
                    continue
                if issubclass(ncl[1], NodeBase):
                    nodeclass_map[ncl[0]] = ncl[1]
        except:
            pass
    return nodeclass_map

def get_processor_consume_map():
    processor_consume_map = {}
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
                    if consumed in processor_consume_map:
                        processor_consume_map[consumed].append(pcl[1])
                    else:
                        processor_consume_map[consumed] = [pcl[1]]
    return processor_consume_map

def get_search_result_processor(url: str) -> SearchProcessorBase:
    all_processor_members = inspect.getmembers(sys.modules["processors"])
    for pm in all_processor_members:
        if not inspect.ismodule(pm[1]):
            continue
        all_pmodule_members = inspect.getmembers(pm[1])
        for pcl in all_pmodule_members:
            if not inspect.isclass(pcl[1]) or pcl[1] is ProcessorBase:
                continue
            if issubclass(pcl[1], SearchProcessorBase):
                regexes = pcl[1].url_regexes
                for regex in regexes:
                    if re.match(regex, url):
                        return pcl[1]