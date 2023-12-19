from nodes import GenericText, NodeBase, Website
from processor import ProcessorBase
from util.domain_util import is_excluded_domain
from dns import *

class DNSProcessor(ProcessorBase):
    consumed_nodetypes = [Website]
    queried_types = [rdatatype.RdataType.CNAME, rdatatype.RdataType.TXT]

    def process(self) -> list[NodeBase]:
        nodes = []
        domain = self._get_domain()
        if is_excluded_domain(domain):
            return []

        for query_type in DNSProcessor.queried_types:
            try:
                res = list(resolver.resolve(domain, query_type))
                for entry in res:
                    print(entry.__class__.__name__)
                    match(entry.__class__.__name__):
                        case "CNAME": nodes.append(Website(entry.target))
                        case "TXT": nodes.append(GenericText(entry.to_text()))
            except:
                pass

        return nodes
    
    def _get_domain(self) -> str:
        match(self.node.__class__.__name__):
            case "Website": return self.node.domain
