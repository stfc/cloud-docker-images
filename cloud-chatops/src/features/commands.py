"""This module handles the posting of messages to Slack using the Slack SDK WebClient class."""

from typing import List
from datetime import datetime, timedelta
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from enum_states import PRsFoundState
from read_data import get_token, get_user_map, get_repos
from get_github_prs import GetGitHubPRs
from pr_dataclass import PrData

# If the PR author is not in the Slack ID mapping
# then we set the user to mention as David Fairbrother
# as the team lead to deal with this PR.
DEFAULT_AUTHOR = "U01JG0LKU3W"
DEFAULT_CHANNEL = "dev-chatops"


class PostToDMs:
    """
    This class handles the Slack posting.
    """

    def __init__(self):
        super().__init__()
        self.repos = get_repos()
        self.client = WebClient(token=get_token("SLACK_BOT_TOKEN"))
        self.slack_ids = get_user_map()
        self.prs = GetGitHubPRs(get_repos(), "stfc").run()
        self.channel = DEFAULT_CHANNEL
        self.thread_ts = None

    def run(self, channel: str, post_all: bool) -> None:
        """
        This method calls the functions to post the reminder message and further PR messages.
        :param channel: The users channel ID to post to.
        :param post_all: To post all PRs found or only ones authored by the user.
        """
        self.channel = channel
        self.post_reminder_message()
        self.post_thread_messages(self.prs, post_all)

    def post_reminder_message(self) -> WebClient.chat_postMessage:
        """
        This method posts the main reminder message to start the thread if PR notifications.
        :return: The reminder message return object
        """
        reminder = self.client.chat_postMessage(
            channel=self.channel,
            text="Here are the outstanding PRs as of today:",
        )
        self.thread_ts = reminder.data["ts"]
        self.channel = reminder.data["channel"]
        return reminder

    def post_thread_messages(self, prs: List[PrData], post_all: bool) -> None:
        """
        This method iterates through each PR and calls the post method for them.
        :param post_all: To post all prs or user only prs.
        :param prs: A list of PRs from GitHub
        """
        prs_posted = PRsFoundState.NONE_FOUND
        for pr in prs:
            checked_pr = self.check_pr(pr)
            prs_posted = self.filter_thread_message(checked_pr, post_all)

        if prs_posted == PRsFoundState.NONE_FOUND:
            self.send_no_prs()

    def filter_thread_message(self, info: PrData, post_all: bool) -> PRsFoundState:
        """
        This method filters which pull requests to send to the thread dependent on the value of personal_thread.
        If personal_thread holds a value, only PRs authored by that user will be sent to the thread.
        Else, all the PRs will be sent.
        :param post_all: To post all PRs or user specific PRs
        :param info: The PR info to send in a message.
        :return: Returns an Enum state.
        """
        pr_author = info.user
        slack_member = self.channel
        if post_all:
            self.send_thread(info)
            return PRsFoundState.PRS_FOUND
        if not post_all and pr_author == slack_member:
            self.send_thread(info)
            return PRsFoundState.PRS_FOUND
        return PRsFoundState.NONE_FOUND

    def send_no_prs(self) -> None:
        """
        This method sends a message to the user that they have no PRs open.
        This method is only called if no other PRs have been mentioned.
        :param reminder: The thread message to send under.
        """
        self.client.chat_postMessage(
            text="There are no outstanding pull requests open.",
            channel=self.channel,
            thread_ts=self.thread_ts,
            unfurl_links=False,
        )

    def check_pr(self, info: PrData) -> PrData:
        """
        This method validates certain information in the PR data such as who authored the PR and if it's old or not.
        :param info: The information to validate.
        :return: The validated information.
        """
        if info.user not in self.slack_ids:
            info.user = DEFAULT_AUTHOR
        else:
            info.user = self._github_to_slack_username(info.user)
        opened_date = datetime.fromisoformat(info.created_at).replace(tzinfo=None)
        datetime_now = datetime.now().replace(tzinfo=None)
        time_cutoff = datetime_now - timedelta(days=30 * 6)
        if opened_date < time_cutoff:
            info.old = True
        del info.created_at
        return info

    def send_thread(self, pr: PrData) -> None:
        """
        This method sends the thread message and prepares the reactions.
        :param pr: PR dataclass
        """
        message = self.construct_message(pr.pr_title, pr.user, pr.url, pr.old)
        response = self.client.chat_postMessage(
            text=message,
            channel=self.channel,
            thread_ts=self.thread_ts,
            unfurl_links=False,
        )
        assert response["ok"]
        pr.thread_ts = response.data["ts"]
        self.send_thread_react(pr)

    def send_thread_react(self, pr: PrData) -> None:
        """
        This method sends reactions to the PR message if necessary.
        """
        react_with = []
        if pr.old:
            react_with.append("alarm_clock")
        if pr.draft:
            react_with.append("scroll")
        for react in react_with:
            react_response = self.client.reactions_add(
                channel=self.channel, name=react, timestamp=pr.thread_ts
            )
            assert react_response["ok"]

    def construct_message(self, pr_title: str, user: str, url: str, old: bool) -> str:
        """
        This method constructs the PR message depending on if the PR is old and if the message should mention or not.
        :param pr_title: The title of the PR.
        :param user: The author of the PR.
        :param url: The URL of the PR.
        :param old: If the PR is older than 6 months.
        :return:
        """
        message = []
        if old:
            message.append("*This PR is older than 6 months. Consider closing it:*")
        message.append(f"Pull Request: <{url}|{pr_title}>")
        name = self._get_real_name(user)
        message.append(f"Author: {name}")
        return "\n".join(message)

    def _get_real_name(self, username: str) -> str:
        """
        This method uses the Slack client method to get the real name of a user and returns it.
        :param username: The user ID to look for
        :return: Returns the real name or if not found the name originally parsed in
        """
        try:
            name = self.client.users_profile_get(user=username)["profile"]["real_name"]
        except SlackApiError:
            name = username
        return name

    def _github_to_slack_username(self, user: str) -> str:
        """
        This method checks if we have a Slack id for the GitHub user and returns it.
        :param user: GitHub username to check for
        :return: Slack ID or GitHub username
        """
        return self.slack_ids[user] if user in self.slack_ids else user
