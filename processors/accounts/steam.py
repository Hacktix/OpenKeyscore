from config import KeyscoreConfig
from nodes import GenericText, Location, NodeBase, Username
from processor import ProcessorBase
import requests
from loguru import logger

from util.html_util import get_bs_for_url

class SteamAccount(NodeBase):
    _type_display_name = "Steam Account"

    id: str = None
    display_name: str = None
    bio: str = None
    url: str = None
    avatar: str = None
    name: str = None
    location: str = None

    def __init__(self, parent: NodeBase = None) -> None:
        super().__init__(parent)

    def equals(self, other: NodeBase): return (self.id == other.id or self.name == other.name) if type(other) == SteamAccount else False
    def __repr__(self): return f"{self.name} ({self.display_name})" if self.name else f"{self.display_name}"

    @staticmethod
    def parse(*args): return SteamAccount(*args)

class SteamProcessor(ProcessorBase):
    consumed_nodetypes = [Username]

    _showed_no_apikey_warning = False

    def process(self) -> list[NodeBase]:
        node = SteamAccount()
        username = self._get_queryable_username()
        api_success = SteamProcessor._add_data_from_api(username, node)
        bs_success = SteamProcessor._add_data_from_bs(username, node)

        if not api_success and not bs_success:
            return []
        return [node]
    
    def _add_data_from_bs(username: str, node: SteamAccount) -> bool:
        bs = get_bs_for_url(f"https://steamcommunity.com/id/{username}")
        node.id = username
        success = False

        if bs.find("div", class_="header_real_name") and bs.find("div", class_="header_real_name").find("bdi"):
            node.name = bs.find("div", class_="header_real_name").find("bdi").get_text()
            lines = bs.find("div", class_="header_real_name").get_text().split("\n")
            node.location = lines[len(lines) - 1].strip()
            success = True
        if bs.find("span", class_="actual_persona_name"):
            node.display_name = bs.find("span", class_="actual_persona_name").get_text()
            success = True
        if bs.find("div", class_="profile_summary"):
            node.bio = bs.find("div", class_="profile_summary").get_text().strip()
            success = True

        return success
    
    def _add_data_from_api(username: str, node: SteamAccount) -> bool:
        api_key = KeyscoreConfig.get("steam_api_key")
        if not api_key:
            if not SteamProcessor._showed_no_apikey_warning:
                SteamProcessor._showed_no_apikey_warning = True
                logger.warning("WARNING: steam_api_key Environment Variable not set. Steam Web API cannot be used")
            return False
        
        id_lookup_res = SteamProcessor._send_request(f"ISteamUser/ResolveVanityURL/v0001/?key={api_key}&vanityurl={username}")
        if id_lookup_res.status_code == 403:
            logger.error("Invalid steam_api_key provided")
            return False
        
        id_res = id_lookup_res.json()["response"]
        if id_res["success"] != 1:
            return False
        
        steam_id = id_res["steamid"]
        profile = SteamProcessor._send_request(f"ISteamUser/GetPlayerSummaries/v0002/?key={api_key}&steamids={steam_id}").json()["response"]["players"][0]
        node.id = steam_id
        node.display_name = profile.get("personaname")
        node.url = profile.get("profileurl")
        node.avatar = profile.get("avatarfull")
        node.name = profile.get("realname")
        return True

    def _get_queryable_username(self) -> str:
        match(self.node.__class__.__name__):
            case "Username": return self.node.username

    def _send_request(path: str):
        return requests.get(f"https://api.steampowered.com/{path}")



class SteamUserProcessor(ProcessorBase):
    consumed_nodetypes = [SteamAccount]
    def process(self):
        user: SteamAccount = self.node
        nodes = []

        if user.display_name: nodes.append(Username(user.display_name))
        if user.bio: nodes.append(GenericText(user.bio))
        if user.location: nodes.append(Location(user.location))

        return nodes