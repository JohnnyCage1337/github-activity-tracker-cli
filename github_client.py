import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from enum import Enum
from typing import Self

from load_env import GITHUB_TOKEN, USER_AGENT


class GithubEventType(str, Enum):
    """Enum type for Github Events Types.

    https://docs.github.com/en/rest/using-the-rest-api/github-event-types?apiVersion=2026-03-10
    """

    # Code
    PUSH = "PushEvent"
    CREATE = "CreateEvent"
    DELETE = "DeleteEvent"
    GOLLUM = "GollumEvent"

    # Pull Request and Code Review
    PULL_REQUEST = "PullRequestEvent"
    PULL_REQUEST_REVIEW = "PullRequestReviewEvent"
    PULL_REQUEST_REVIEW_COM = "PullRequestReviewCommentEvent"
    COMMIT_COMMENT = "CommitCommentEvent"

    # Discussions, issues
    ISSUES = "IssuesEvent"
    ISSUE_COMMENT = "IssueCommentEvent"
    DISCUSSION = "DiscussionEvent"

    # Github social
    WATCH = "WatchEvent"
    FORK = "Forkevent"
    MEMBER = "MemberEvent"
    PUBLIC = "PublicEvent"

    # Deploy and Release
    RELEASE = "ReleaseEvent"

    UNKNOWN = "UnknownEvent"

    @classmethod
    def from_str(cls, event: "str") -> Self:
        try:
            return cls(event)
        except ValueError:
            return cls.UNKNOWN


@dataclass
class GithubEvent:
    repo_name: str
    event_type: GithubEventType
    payload: dict


class GithubClient:
    """Class response for connecting with API and creating dataclasses objects."""

    BASE_URL = "https://api.github.com/users/{username}/events"

    def __init__(self, username="JohnnyCage1337"):
        self._username = username

    @property
    def username(self):
        return self._username

    def _call_api(self) -> list[dict]:
        """Fetching from Github API raw json about user acitivity."""

        current_url = self.BASE_URL.format(username=self.username)

        req = urllib.request.Request(current_url)
        req.add_header("User-Agent", f"{USER_AGENT or 'github-activity-cli'}")
        req.add_header("Accept", "application/vnd.github+json")
        req.add_header("X-Github-Api-Version", "2026-03-10")

        if GITHUB_TOKEN:
            req.add_header("Authorization", f"Bearer {GITHUB_TOKEN}")

        try:
            with urllib.request.urlopen(req) as response:
                raw_json = json.loads(response.read().decode("utf-8"))
                with open("mock.json", "w") as f:
                    json.dump(raw_json, f, indent=4)
                return raw_json
        except Exception as e:
            raise e

    def _parse_raw_json(self, raw_json: list[dict]) -> list[GithubEvent]:
        """Parse raw json data to dataclass list."""

        events = []
        for item in raw_json:
            repo_name = item.get("repo", {}).get("name", "undefined_name")
            event_type = GithubEventType.from_str(item.get("type", ""))
            if event_type == GithubEventType.UNKNOWN:
                print("UNKNOWN event detected")
            payload = item.get("payload", {})

            new_event = GithubEvent(repo_name, event_type, payload)
            events.append(new_event)

        return events

    def fetch_data(self):
        return self._parse_raw_json(self._call_api())


if __name__ == "__main__":
    client = GithubClient()
    print(client.fetch_data())
