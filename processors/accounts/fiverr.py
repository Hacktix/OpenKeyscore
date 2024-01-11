from loguru import logger
from requests import HTTPError
from nodes import GenericText, Location, NodeBase, Username
from processor import ProcessorBase, SearchProcessorBase
import re
from selenium.webdriver.common.by import By
from util.html_util import get_bs_for_url

class FiverrAccount(NodeBase):
    _type_display_name = "Fiverr Account"

    def __init__(self, username: str, display_name: str, bio: str, location: str, parent: NodeBase = None) -> None:
        super().__init__(parent)
        self.username = username
        self.display_name = display_name
        self.bio = bio
        self.location = location

    def equals(self, other: NodeBase): return self.username == other.username if type(other) == FiverrAccount else False
    def __repr__(self): return f"{self.display_name} ({self.username})" if self.display_name else f"{self.username}"

    @staticmethod
    def parse(*args): return FiverrAccount(*args)

class FiverrProcessor(ProcessorBase):
    consumed_nodetypes = [Username]
    captcha_block = False

    def process(self) -> list[NodeBase]:
        if FiverrProcessor.captcha_block:
            return []
        
        username = self._get_queryable_username()
        try:
            bs = get_bs_for_url(
                f"https://fiverr.com/{username.lower()}",
                load_check=lambda driver: len(driver.find_elements(By.CLASS_NAME, "HIEH1Ol")) > 0 or len(driver.find_elements(By.CLASS_NAME, "not-found-page")) > 0 or len(driver.find_elements(By.ID, "px-captcha")) > 0,
                post_load=lambda driver: driver.find_element(By.CLASS_NAME, "HIEH1Ol").click(),
                ready_check=lambda driver: driver.find_element(By.CLASS_NAME, "dsboZim")
            )
            if bs.find("div", id="px-captcha"):
                FiverrProcessor.captcha_block = True
                raise Exception("Site prompted for captcha")

            display_name = bs.find("h1", class_="co-text-darkest").get_text() if bs.find("h1", class_="co-text-darkest") else None
            username = bs.find("div", class_="bD8FFIr").get_text()[1:] if bs.find("div", class_="bD8FFIr") else None
            location = bs.find_all("span", class_="m-l-8")[1].get_text() if bs.find_all("span", class_="m-l-8") else None
            bio = bs.find("div", class_="vxWK_SR").get_text().strip() if bs.find("div", class_="vxWK_SR") else None
            
            account_node = FiverrAccount(username, display_name, bio, location)
            return [account_node]
        except HTTPError as e:
            if e.response.status_code != 404:
                logger.error(f"Fiverr responded with Error Code {e.response.status_code}")
        except Exception as e:
            logger.error(f"Fiverr Lookup failed: {type(e).__name__}: {e}")

        return []

    def _get_queryable_username(self) -> str:
        match(self.node.__class__.__name__):
            case "Username": return self.node.username
    
class FiverrSearchProcessor(SearchProcessorBase):
    url_regexes = [r"https?:\/\/(?:.+\.)?fiverr\.com\/(\w+)\/?.*"]

    def get_nodes_from_search_result(url: str):
        username = re.match(FiverrSearchProcessor.url_regexes[0], url)
        username_node = Username(username.group(1))
        return FiverrProcessor(username_node).process()



class FiverrUserProcessor(ProcessorBase):
    consumed_nodetypes = [FiverrAccount]
    def process(self):
        user: FiverrAccount = self.node
        nodes = []

        if user.display_name: nodes.append(Username(user.display_name))
        if user.username: nodes.append(Username(user.username))
        if user.bio: nodes.append(GenericText(user.bio))
        if user.location: nodes.append(Location(user.location))

        return nodes