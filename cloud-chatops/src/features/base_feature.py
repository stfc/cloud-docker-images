"""
This module is the feature base class.
All features should inherit this class to reduce code duplication.
"""

from slack_sdk.errors import SlackApiError
from dateutil import parser as datetime_parser
from read_data import get_token, get_repos, get_user_map
from get_github_prs import GetGitHubPRs
from pr_dataclass import PrData
from slack_sdk import WebClient
from datetime import datetime, timedelta
from dataclasses import replace

# If the PR author is not in the Slack ID mapping
# then we set the author as a default value.
DEFAULT_AUTHOR = "U01JG0LKU3W"  # David Fairbrother
DEFAULT_CHANNEL = "C06U37Y02R4"  # "dev-chatops" channel as default
DEFAULT_REPO_OWNER = "stfc"  # Our repos are owned by "stfc"


class BaseFeature:
    """This base class provides universal methods for features."""

    channel: str

    def __init__(self):
        self.channel = DEFAULT_CHANNEL
        self.client = WebClient(token=get_token("SLACK_BOT_TOKEN"))
        self.prs = GetGitHubPRs(get_repos(), DEFAULT_REPO_OWNER).run()
        self.slack_ids = get_user_map()

    def _github_to_slack_username(self, user: str) -> str:
        """
        This method translates the Slack member id to GitHub user.
        :param user: GitHub username to check for
        :return: Slack ID or GitHub username
        """
        return self.slack_ids[user] if user in self.slack_ids else user

    def _slack_to_human_username(self, slack_member_id: str) -> str:
        """
        This method gets the display username from a Slack member ID
        :param slack_member_id: The Slack member ID to look for
        :return: Returns the real name or if not found the name originally parsed in
        """
        try:
            name = self.client.users_profile_get(user=slack_member_id)["profile"][
                "real_name"
            ]
        except SlackApiError:
            name = slack_member_id
        return name

    def _post_reminder_message(self) -> str:
        """
        This method posts the main reminder message to start the thread of PR notifications.
        :return: The reminder message object
        """
        reminder = self.client.chat_postMessage(
            channel=self.channel,
            text="Here are the outstanding PRs as of today:",
        )
        assert reminder["ok"]
        return reminder.data["ts"]

    def _send_no_prs_found(self, thread_ts) -> None:
        """
        This method sends a message to the chat that there are no PRs.
        :param thread_ts: Timestamp of reminder message
        """
        response = self.client.chat_postMessage(
            text="There are no outstanding pull requests open.",
            channel=self.channel,
            thread_ts=thread_ts,
            unfurl_links=False,
        )
        assert response["ok"]

    def _send_thread(
        self, pr_data: PrData, thread_ts: str
    ) -> WebClient.chat_postMessage:
        """
        This method sends the message and returns the response.
        :param pr_data: The PR data as a dataclass
        :param thread_ts: Timestamp of reminder message
        :return: The message response.
        """
        message = PRMessageBuilder().make_message(pr_data)
        response = self.client.chat_postMessage(
            text=message,
            channel=self.channel,
            thread_ts=thread_ts,
            unfurl_links=False,
        )
        assert response["ok"]
        return response

    def _send_thread_react(self, pr: PrData, channel: str, thread_ts: str) -> None:
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
                channel=channel, name=react, timestamp=thread_ts
            )
            assert react_response["ok"]


class PRMessageBuilder(BaseFeature):
    """This class handles constructing the PR messages to be sent."""

    # pylint: disable=R0903
    # Disabling this as there only needs to be one entry point.
    def make_message(self, pr_data: PrData) -> str:
        """
        This method checks the pr data and makes a string message from it.
        :param pr_data: The PR info
        :return: The message to post
        """
        checked_info = self._check_pr_info(pr_data)
        return self._construct_string(checked_info)

    def _construct_string(self, pr_data: PrData) -> str:
        """
        This method constructs the PR message depending on if the PR is old and if the message should mention or not.
        :param pr_data: The data class containing the info about the PR.
        :return: The message as a single string.
        """
        message = []
        if pr_data.old:
            message.append("*This PR is older than 6 months. Consider closing it:*")
        message.append(f"Pull Request: <{pr_data.url}|{pr_data.pr_title}>")
        name = self._slack_to_human_username(pr_data.user)
        message.append(f"Author: {name}")
        return "\n".join(message)

    @staticmethod
    def _check_pr_age(time_created: str) -> bool:
        """
        This method checks if the PR is older than 6 months.
        :param time_created: The date the PR was created.
        :return: PR older or not.
        """
        opened_date = datetime_parser.parse(time_created).replace(tzinfo=None)
        datetime_now = datetime.now().replace(tzinfo=None)
        time_cutoff = datetime_now - timedelta(days=30 * 6)
        return opened_date < time_cutoff

    def _check_pr_info(self, info: PrData) -> PrData:
        """
        This method validates certain information in the PR data such as who authored the PR and if it's old or not.
        :param info: The information to validate.
        :return: The validated information.
        """
        new_info = replace(
            info,
            user=self._github_to_slack_username(info.user),
            old=self._check_pr_age(info.created_at),
        )
        return new_info
