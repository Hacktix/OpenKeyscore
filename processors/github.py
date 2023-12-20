from nodes import Email, NodeBase, RealName, Username, Website
from processor import ProcessorBase
import requests

class GithubAccount(NodeBase):
    _type_display_name = "GitHub Account"

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

    def equals(self, other: NodeBase): return self.username == other.username if type(other) == GithubAccount else False
    def __repr__(self): return f"{self.display_name} ({self.username})" if self.display_name else f"{self.username}"

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
        return [user_node]

    def _get_queryable_username(self) -> str:
        match(self.node.__class__.__name__):
            case "Username": return self.node.username

    def _send_request(path: str):
        return requests.get(f"https://api.github.com/{path}")
    


class GithubUserProcessor(ProcessorBase):
    consumed_nodetypes = [GithubAccount]
    def process(self):
        user = self.node
        nodes = []

        if user.email: nodes.append(Email(user.email, user))
        if user.website: nodes.append(Website(user.website, user))
        if user.display_name and " " in user.display_name: nodes.append(RealName(user.display_name, user))

        return nodes
    


class GithubEventProcessor(ProcessorBase):
    consumed_nodetypes = [GithubAccount]
    def process(self):
        user = self.node
        nodes = []

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
                name_node = RealName(username, user)
            else:
                name_node = Username(username, user)
            nodes.append(name_node)
        
        return nodes



class GithubRepoProcessor(ProcessorBase):
    consumed_nodetypes = [GithubAccount]
    def process(self):
        username = self.node.username
        repo_res = GithubProcessor._send_request(f"users/{username}/repos")
        if repo_res.status_code != 200:
            return []
        repos = repo_res.json()

        nodes = []
        for repo in repos:
            if repo["fork"]:
                continue
            if repo["homepage"] and "github." not in repo["homepage"] and "githubusercontent." not in repo["homepage"]:
                nodes.append(Website(repo["homepage"]))
        return nodes