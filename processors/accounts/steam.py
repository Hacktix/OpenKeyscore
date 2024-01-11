from nodes import GenericText, Location, NodeBase, Username
from processor import ProcessorBase
import requests

from util.html_util import get_bs_for_url
from selenium.webdriver.common.by import By

class SteamAccount(NodeBase):
    _type_display_name = "Steam Account"

    id: str = None
    display_name: str = None
    bio: str = None
    url: str = None
    avatar: str = None
    name: str = None
    location: str = None
    aliases: list[str] = []

    def __init__(self, parent: NodeBase = None) -> None:
        super().__init__(parent)

    def equals(self, other: NodeBase): return (self.id == other.id or self.name == other.name) if type(other) == SteamAccount else False
    def __repr__(self): return f"{self.name} ({self.display_name})" if self.name else f"{self.display_name}"

    @staticmethod
    def parse(*args): return SteamAccount(*args)

class SteamProcessor(ProcessorBase):
    consumed_nodetypes = [Username]

    def process(self) -> list[NodeBase]:
        node = SteamAccount()
        username = self._get_queryable_username()
        success = SteamProcessor._add_data_from_bs(username, node)

        if not success:
            return []
        return [node]
    
    def _add_data_from_bs(username: str, node: SteamAccount) -> bool:
        bs = get_bs_for_url(
            f"https://steamcommunity.com/id/{username}",
            load_check=lambda driver: len(driver.find_elements(By.CLASS_NAME, "actual_persona_name")) > 0 or len(driver.find_elements(By.CLASS_NAME, "error_ctn")) > 0,
            post_load=lambda driver: driver.find_element(By.ID, "getnamehistory_arrow").click(),
            ready_check=lambda driver: driver.find_element(By.ID, "NamePopupAliases") and len(driver.find_elements(By.CSS_SELECTOR, ".NamePopupAliases > img")) == 0
        )
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
        if bs.find("div", id="NamePopupAliases"):
            alias_elements = list(bs.find("div", id="NamePopupAliases").children)
            aliases = list(map(lambda e: e.get_text(), alias_elements))
            if "This user has no known aliases" in aliases:
                aliases.remove("This user has no known aliases")
            node.aliases = aliases

        return success

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

        for alias in user.aliases:
            nodes.append(Username(alias))

        return nodes