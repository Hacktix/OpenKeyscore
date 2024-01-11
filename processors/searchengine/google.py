from loguru import logger
from nodes import NodeBase, Username
from processor import ProcessorBase
from googlesearch import search
from util.module_util import get_search_result_processor

class GoogleProcessor(ProcessorBase):
    consumed_nodetypes = [Username]

    def process(self) -> list[NodeBase]:
        username = self._get_queryable_username()
        try:
            results = search(f'"{username}"', sleep_interval=1)
            nodes = []
            for result in results:
                processor = get_search_result_processor(result)
                logger.debug(f"Processing search result {result.url} with {processor.__class__.__name__}")
                if processor:
                    nodes = nodes + processor.get_nodes_from_search_result(result)
            return nodes
        except Exception as e:
            logger.error(f"Google Lookup failed: {e}")
            return []

    def _get_queryable_username(self) -> str:
        match(self.node.__class__.__name__):
            case "Username": return self.node.username