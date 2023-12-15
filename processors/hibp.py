from config import KeyscoreConfig
from nodes import Email, NodeBase
from processor import ProcessorBase
import requests

class DataBreach(NodeBase):
    def __init__(self, name: str, parent: NodeBase = None) -> None:
        super().__init__(parent)
        self.name = name

    def equals(self, other: NodeBase): return self.name == other.name if type(other) == DataBreach else False
    def __repr__(self): return self.name

    @staticmethod
    def parse(*args): return DataBreach(args[0])

class HIBPProcessor(ProcessorBase):
    consumed_nodetypes = [Email]

    _showed_no_apikey_warning = False

    def process(self) -> list[NodeBase]:
        if KeyscoreConfig.get("hibp_api_key") is None:
            if not HIBPProcessor._showed_no_apikey_warning:
                HIBPProcessor._showed_no_apikey_warning = True
                print("WARNING: hibp_api_key Environment Variable not set. HaveIBeenPwned cannot be used")
            return []
        
        accountname = self._get_queryable_username()
        hibp_res = HIBPProcessor._send_request(f"breachedaccount/{accountname}")
        
        if hibp_res.status_code == 401:
            print("ERROR: Invalid hibp_api_key provided")
            return []
        
        if hibp_res.status_code == 200:
            breaches = hibp_res.json()
            return list(map(lambda breach: DataBreach(breach["Name"]), breaches))
        return []
    
    def _get_queryable_username(self) -> str:
        match(self.node.__class__.__name__):
            case "Email": return self.node.email.value

    def _send_request(path: str):
        headers = {"hibp-api-key": KeyscoreConfig.get("hibp_api_key")}
        return requests.get(f"https://haveibeenpwned.com/api/v3/{path}", headers=headers)