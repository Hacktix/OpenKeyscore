from loguru import logger
from requests import HTTPError
from config import KeyscoreConfig
from nodes import GenericText, Location, NodeBase, Username, Website
from processor import ProcessorBase, SearchProcessorBase
import re
from selenium.webdriver.common.by import By
from selenium.webdriver import Chrome
from util.html_util import get_bs_for_url
import time

class YoutubeAccount(NodeBase):
    _type_display_name = "YouTube Channel"

    def __init__(self, username: str, display_name: str, bio: str, location: str, links: list[str], parent: NodeBase = None) -> None:
        super().__init__(parent)
        self.username = username
        self.display_name = display_name
        self.bio = bio
        self.location = location
        self.links = links

    def equals(self, other: NodeBase): return self.username == other.username if type(other) == YoutubeAccount else False
    def __repr__(self): return f"{self.display_name} ({self.username})" if self.display_name else f"{self.username}"

    @staticmethod
    def parse(*args): return YoutubeAccount(*args)

class YoutubeChannelId(NodeBase):
    _type_display_name = "YouTube Channel ID"

    def __init__(self, id: str, parent: NodeBase = None) -> None:
        super().__init__(parent)
        self.id = id

    def equals(self, other: NodeBase): return self.id == other.id if type(other) == YoutubeChannelId else False
    def __repr__(self): return self.id

    @staticmethod
    def parse(*args): return YoutubeAccount(*args)

class YoutubeProcessor(ProcessorBase):
    consumed_nodetypes = [Username, YoutubeChannelId]

    def process(self) -> list[NodeBase]:        
        username = self._get_queryable_username()

        def youtube_post_load(driver: Chrome):
            """Specialized post-load function to navigate past cookies popup on YouTube."""
            if len(driver.find_elements(By.CLASS_NAME, "gOOQJb")) > 0:
                driver.find_elements(By.CLASS_NAME, "VfPpkd-LgbsSe")[5].click()
                while len(driver.find_elements(By.CLASS_NAME, "ytd-channel-tagline-renderer")) == 0 and driver.title != "404 Not Found":
                    time.sleep(KeyscoreConfig.get("html_default_wait"))
            driver.find_element(By.CLASS_NAME, "ytd-channel-tagline-renderer").click()

        try:
            bs = get_bs_for_url(
                f"https://youtube.com/{username}",
                load_check=lambda driver: len(driver.find_elements(By.CLASS_NAME, "ytd-channel-tagline-renderer")) > 0 or driver.title == "404 Not Found" or len(driver.find_elements(By.CLASS_NAME, "gOOQJb")) > 0,
                post_load=youtube_post_load,
                ready_check=lambda driver: driver.find_element(By.ID, "description-container")
            )
            if bs.find("title").get_text() == "404 Not Found":
                return []

            display_name = bs.find("yt-formatted-string", class_="ytd-channel-name").get_text()
            username = bs.find("yt-formatted-string", id="channel-handle").get_text()
            location = None # TODO: Figure out how to extract this properly
            bio = bs.find("yt-attributed-string", id="description-container").get_text()
            links = [] # TODO: Figure out how to extract this properly
            
            account_node = YoutubeAccount(username, display_name, bio, location, links)
            return [account_node]
        except HTTPError as e:
            if e.response.status_code != 404:
                logger.error(f"YouTube responded with Error Code {e.response.status_code}")
        except Exception as e:
            logger.error(f"YouTube Lookup failed: {type(e).__name__}: {e}")

        return []

    def _get_queryable_username(self) -> str:
        match(self.node.__class__.__name__):
            case "Username": return f"@{self.node.username}"
            case "YoutubeChannelId": return f"channel/{self.node.id}"
    
class YoutubeSearchProcessor(SearchProcessorBase):
    url_regexes = [
        r"https?:\/\/(?:.+\.)?youtube\.com\/@([\w\-]+)\/?.*",        # Handle URL
        r"https?:\/\/(?:.+\.)?youtube\.com\/channel\/([\w\-]+)\/?.*" # Channel ID Url
    ]

    def get_nodes_from_search_result(url: str):
        if re.match(YoutubeSearchProcessor.url_regexes[0], url):
            username = re.match(YoutubeSearchProcessor.url_regexes[0], url)
            username_node = Username(username.group(1))
            return YoutubeProcessor(username_node).process()
        elif re.match(YoutubeSearchProcessor.url_regexes[1], url):
            id = re.match(YoutubeSearchProcessor.url_regexes[1], url)
            id_node = YoutubeChannelId(id.group(1))
            return YoutubeProcessor(id_node).process()



class YoutubeUserProcessor(ProcessorBase):
    consumed_nodetypes = [YoutubeAccount]
    def process(self):
        user: YoutubeAccount = self.node
        nodes = []

        if user.display_name: nodes.append(Username(user.display_name))
        if user.username: nodes.append(Username(user.username))
        if user.bio: nodes.append(GenericText(user.bio))
        if user.location: nodes.append(Location(user.location))
        if user.links:
            for link in user.links:
                nodes.append(Website(link))

        return nodes