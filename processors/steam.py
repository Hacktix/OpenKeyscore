from config import KeyscoreConfig
from nodes import Email, NodeBase, Username, Website
from processor import ProcessorBase
import requests
from datetime import datetime

class SteamAccount(NodeBase):
    def __init__(self, id: str, display_name: str, url: str, avatar: str, lastonline: int, name: str, created: int, country: str, state: str, parent: NodeBase = None) -> None:
        super().__init__(parent)
        self.id = id
        self.display_name = display_name
        self.url = url
        self.avatar = avatar
        self.lastonline = datetime.fromtimestamp(lastonline) if lastonline else None
        self.name = name
        self.created = datetime.fromtimestamp(created) if created else None
        self.country = country
        self.state = state

    def equals(self, other: NodeBase): return self.id == other.id if type(other) == SteamAccount else False
    def __repr__(self): return f"{self.name} ({self.display_name}) : {self.url}" if self.name else f"{self.display_name} : {self.url}"

    @staticmethod
    def parse(*args): return SteamAccount(*args)

class SteamProcessor(ProcessorBase):
    consumed_nodetypes = [Username]

    _showed_no_apikey_warning = False

    def process(self) -> list[NodeBase]:
        api_key = KeyscoreConfig.get("steam_api_key")
        if not api_key:
            if not SteamProcessor._showed_no_apikey_warning:
                SteamProcessor._showed_no_apikey_warning = True
                print("WARNING: steam_api_key Environment Variable not set. Steam Web API cannot be used")
            return []
        
        username = self._get_queryable_username()
        id_lookup_res = SteamProcessor._send_request(f"ISteamUser/ResolveVanityURL/v0001/?key={api_key}&vanityurl={username}")
        
        if id_lookup_res.status_code == 403:
            print("ERROR: Invalid steam_api_key provided")
            return []
        
        id_res = id_lookup_res.json()["response"]
        if id_res["success"] != 1:
            return []
        
        steam_id = id_res["steamid"]
        profile = SteamProcessor._send_request(f"ISteamUser/GetPlayerSummaries/v0002/?key={api_key}&steamids={steam_id}").json()["response"]["players"][0]
        account_node = SteamAccount(
            id=steam_id, display_name=profile.get("personaname"), url=profile.get("profileurl"), avatar=profile.get("avatarfull"), lastonline=profile.get("lastlogoff"),
            name=profile.get("realname"), created=profile.get("timecreated"), country=profile.get("loccountrycode"), state=profile.get("locstatecode")
        )

        return [account_node]

    def _get_queryable_username(self) -> str:
        match(self.node.__class__.__name__):
            case "Username": return self.node.username

    def _send_request(path: str):
        return requests.get(f"https://api.steampowered.com/{path}")