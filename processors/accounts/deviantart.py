from loguru import logger
from requests import HTTPError, TooManyRedirects
from nodes import Location, NodeBase, Username
from processor import ProcessorBase, SearchProcessorBase
import re

from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from util.html_util import get_bs_for_url

class DeviantArtAccount(NodeBase):
    _type_display_name = "DeviantArt Account"

    def __init__(self, username: str, url: str, display_name: str, location: str, parent: NodeBase = None) -> None:
        super().__init__(parent)
        self.username = username
        self.url = url
        self.display_name = display_name
        self.location = location

    def equals(self, other: NodeBase): return self.username == other.username if type(other) == DeviantArtAccount else False
    def __repr__(self): return f"{self.display_name} ({self.username})" if self.display_name else f"{self.username}"

    @staticmethod
    def parse(*args): return DeviantArtAccount(*args)

class DeviantArtProcessor(ProcessorBase):
    consumed_nodetypes = [Username]

    def process(self) -> list[NodeBase]:
        username = self._get_queryable_username()
        try:
            user_url = f"https://deviantart.com/{username}"
            user_bs = get_bs_for_url(
                user_url,
                load_check=lambda driver: driver.find_element(By.CLASS_NAME, "user-link"),
                post_load=lambda driver: driver.find_element(By.LINK_TEXT, "About").click(),
                ready_check=lambda driver: driver.find_element(By.ID, "about")
            )

            username = list(user_bs.find("h1", class_="_38K3K").children)[0]["data-username"]
            display_name_node = user_bs.find("div", class_="_33syq")
            display_name = None if display_name_node is None else display_name_node.get_text()
            location_node = user_bs.find("span", class_="_2cHeo")
            location = None if location_node is None else location_node.get_text()
            user_node = DeviantArtAccount(username, user_url, display_name, location)
            return [user_node]
        except TooManyRedirects: # This happens on 404s apparently
            return []
        except HTTPError as e:
            if e.response.status_code != 404:
                logger.error(f"DeviantArt responded with Error Code {e.response.status_code}")
        except Exception as e:
            logger.error(f"DeviantArt Lookup failed: {type(e).__name__}: {e}")

        return []

    def _get_queryable_username(self) -> str:
        match(self.node.__class__.__name__):
            case "Username": return self.node.username
    
class DeviantArtSearchProcessor(SearchProcessorBase):
    url_regexes = [r"https?:\/\/(?:www\.)?deviantart\.com\/(\w+)\/?.*"]

    def get_nodes_from_search_result(url: str):
        username = re.match(DeviantArtSearchProcessor.url_regexes[0], url)
        username_node = Username(username.group(1))
        return DeviantArtProcessor(username_node).process()



class DeviantArtUserProcessor(ProcessorBase):
    consumed_nodetypes = [DeviantArtAccount]
    def process(self):
        user: DeviantArtAccount = self.node
        nodes = []

        if user.username: nodes.append(Username(user.username))
        if user.display_name: nodes.append(Username(user.display_name))
        if user.location: nodes.append(Location(user.location))

        return nodes