from nodes import NodeBase, Username
from processor import ProcessorBase
import requests

class GithubAccount(NodeBase):
    def __init__(self, username: str, avatar: str, url: str, display_name: str, company: str, website: str, location: str, email: str, bio: str, twitter: str, created: str, parent: NodeBase = None) -> None:
        super().__init__(parent)
        self.username = username
        self.avatar = avatar
        self.url = url
        self.display_name = display_name
        self.company = company
        self.website = website
        self.location = location
        self.email = email
        self.bio = bio
        self.twitter = twitter
        self.created = created

    def equals(self, other: NodeBase): return self.username.value == other.username.value if type(other) == GithubAccount else False
    def __repr__(self): return f"{self.display_name} ({self.username}) : {self.url}" if self.display_name else f"{self.username} : {self.url}"

    @staticmethod
    def parse(*args): return GithubAccount(*args)

class GithubProcessor(ProcessorBase):
    consumed_nodetypes = [Username]

    def process(self) -> list[NodeBase]:
        username = self.get_queryable_username()
        user_response = GithubProcessor.send_request(f"users/{username}")
        if user_response.status_code != 200:
            return []
        user = user_response.json()

        user_node = GithubAccount(
            username=user["login"], avatar=user["avatar_url"], url=user["html_url"], display_name=user["name"], company=user["company"],
            website=user["blog"], location=user["location"], email=user["email"], bio=user["bio"], twitter=user["twitter_username"], created=user["created_at"]
        )
        return [user_node]

    def get_queryable_username(self) -> str:
        match(self.node.__class__.__name__):
            case "Username": return self.node.username.value

    def send_request(path: str):
        return requests.get(f"https://api.github.com/{path}")