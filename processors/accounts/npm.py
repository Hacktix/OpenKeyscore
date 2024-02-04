from nodes import NodeBase, Username
from processor import ProcessorBase
from selenium.webdriver.common.by import By

from util.html_util import get_bs_for_url

class NPMAccount(NodeBase):
    _type_display_name = "NPM Account"

    def __init__(self, username: str, display_name: str, parent: NodeBase = None) -> None:
        super().__init__(parent)
        self.username = username
        self.display_name = display_name
        self.url = f"https://www.npmjs.com/~{username}"

    def equals(self, other: NodeBase): return self.username == other.username if type(other) == NPMAccount else False
    def __repr__(self): return f"{self.display_name} ({self.username})" if self.display_name else f"{self.username}"

    @staticmethod
    def parse(*args): return NPMAccount(*args)

class NPMProcessor(ProcessorBase):
    consumed_nodetypes = [Username]

    def process(self) -> list[NodeBase]:
        username = self._get_queryable_username().lower()
        bs = get_bs_for_url(
            f"https://www.npmjs.com/~{username}",
            load_check=lambda driver: len(driver.find_elements(By.CLASS_NAME, "b219ea1a")) > 0 or len(driver.find_elements(By.CLASS_NAME, "mw6-ns")) > 0
        )
        
        if bs.find("img", class_="mw6-ns"):
            return []
        
        display_name = bs.find("div", class_="mv2").get_text()
        user_node = NPMAccount(username, display_name)
        return [user_node]

    def _get_queryable_username(self) -> str:
        match(self.node.__class__.__name__):
            case "Username": return self.node.username