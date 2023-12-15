from nodes import Email, NodeBase, Username, Website
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
        username = self._get_queryable_username()
        user_response = GithubProcessor._send_request(f"users/{username}")
        if user_response.status_code != 200:
            return []
        user = user_response.json()

        user_node = GithubAccount(
            username=user["login"], avatar=user["avatar_url"], url=user["html_url"], display_name=user["name"], company=user["company"],
            website=user["blog"], location=user["location"], email=user["email"], bio=user["bio"], twitter=user["twitter_username"], created=user["created_at"]
        )
        return [user_node] + self._get_nodes_from_user(user_node)
    
    def _get_nodes_from_user(self, user: GithubAccount) -> list[NodeBase]:
        nodes = []

        if user.email: nodes.append(Email(user.email, user))
        if user.website: nodes.append(Website(user.website, user))

        events_responses = GithubProcessor._send_request(f"users/{user.username}/events")
        events_responses.raise_for_status()
        events = events_responses.json()

        commit_emails = []
        commit_usernames = []
        for event in events:
            match event["type"]:
                case "PushEvent":
                    for commit in event["payload"]["commits"]:
                        commit_email = commit["author"]["email"]
                        if commit_email not in commit_emails:
                            commit_emails.append(commit_email)
                        commit_username = commit["author"]["name"]
                        if commit_username not in commit_usernames:
                            commit_usernames.append(commit_username)

        for email in commit_emails:
            if "users.noreply.github.com" in email:
                continue
            email_node = Email(email, user)
            nodes.append(email_node)
        for username in commit_usernames:
            if " " in username:
                continue
            username_node = Username(username, user)
            nodes.append(username_node)
        
        return nodes

    def _get_queryable_username(self) -> str:
        match(self.node.__class__.__name__):
            case "Username": return self.node.username.value

    def _send_request(path: str):
        return requests.get(f"https://api.github.com/{path}")