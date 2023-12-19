from nodes import NodeBase, Username
from processor import ProcessorBase
from datetime import datetime
import requests

class RedditAccount(NodeBase):
    def __init__(self, username: str, display_name: str, url: str, created: int, parent: NodeBase = None) -> None:
        super().__init__(parent)
        self.username = username
        self.display_name = display_name
        self.url = url
        self.created = datetime.fromtimestamp(created) if created else None

    def equals(self, other: NodeBase): return self.username == other.username if type(other) == RedditAccount else False
    def __repr__(self): return f"{self.display_name} ({self.username}) : {self.url}" if self.display_name else f"{self.username} : {self.url}"

    @staticmethod
    def parse(*args): return RedditAccount(*args)

class RedditProcessor(ProcessorBase):
    consumed_nodetypes = [Username]

    def process(self) -> list[NodeBase]:
        user_res = RedditProcessor._send_request(f"user/{self._get_queryable_username()}/about.json")
        if user_res.status_code != 200:
            return []
        user_data = user_res.json()["data"]
        
        user_node = RedditAccount(
            username=user_data["name"], display_name=user_data["subreddit"]["title"], url=f"https://reddit.com{user_data['subreddit']['url']}",
            created=user_data["created"]
        )

        return [user_node]

    def _get_queryable_username(self) -> str:
        match(self.node.__class__.__name__):
            case "Username": return self.node.username

    def _send_request(path: str):
        return requests.get(f"https://reddit.com/{path}")