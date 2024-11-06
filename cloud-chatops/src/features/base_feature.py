"""
This module is the feature base class.
All features should inherit this class to reduce code duplication.
"""

from abc import ABC
from typing import List
from datetime import datetime, timedelta
from dataclasses import replace
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from read_data import get_token, get_config
from get_github_prs import GetGitHubPRs
from pr_dataclass import PrData
from errors import FailedToPostMessage, UserNotFound


# If the PR author is not in the Slack ID mapping
# then we set the author as a default value.
DEFAULT_AUTHOR = "U01JG0LKU3W"  # David Fairbrother
DEFAULT_CHANNEL = "C06U37Y02R4"  # "dev-chatops" channel as default
DEFAULT_REPO_OWNER = "stfc"  # Our repos are owned by "stfc"


class BaseFeature(ABC):
    """This base abstract class provides universal methods for features."""

    # pylint: disable=R0903
    # This is a base feature and not intended to be used on its own
    channel: str

    def __init__(self):
        self.channel = DEFAULT_CHANNEL
        self.client = WebClient(token=get_token("SLACK_BOT_TOKEN"))
        self.prs = GetGitHubPRs(get_config("repos")).run()
        self.slack_ids = get_config("user-map")

    def _post_reminder_message(self) -> str:
        """
        This method posts the main reminder message to start the thread of PR notifications.
        :return: The reminder message object
        """
        reminder = self.client.chat_postMessage(
            channel=self.channel,
            text="Here are the outstanding PRs as of today:",
        )
        if not reminder["ok"]:
            raise FailedToPostMessage(
                '"ok" must be True otherwise message failed. Same as HTTP 200'
            )
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
        if not response["ok"]:
            raise FailedToPostMessage(
                '"ok" must be True otherwise message failed. Same as HTTP 200'
            )

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
        if not response["ok"]:
            raise FailedToPostMessage(
                '"ok" must be True otherwise message failed. Same as HTTP 200'
            )
        return response

    def _send_thread_react(self, pr: PrData, channel: str, thread_ts: str) -> None:
        """
        This method sends reactions to the PR message if necessary.
        """
        react_with = []
        if pr.old:
            react_with.append("alarm_clock")
        if pr.draft:
            react_with.append("building_construction")
        for react in react_with:
            react_response = self.client.reactions_add(
                channel=channel, name=react, timestamp=thread_ts
            )
            if not react_response["ok"]:
                raise FailedToPostMessage(
                    '"ok" must be True otherwise message failed. Same as HTTP 200'
                )

    @staticmethod
    def _format_prs(prs: List[PrData]) -> List[PrData]:
        """This method runs checks against the prs given and changes values such as old and author."""
        formatted_prs = []
        for pr in prs:
            formatted_prs.append(PRMessageBuilder().add_user_info_and_age(pr))
        return formatted_prs

    def validate_user(self, user: str) -> None:
        """Validate that the given user is in the workspace."""
        try:
            self.client.users_profile_get(user=user)
        except SlackApiError as exc:
            raise UserNotFound(
                f"The user with member ID {user} is not in this workspace."
            ) from exc


class PRMessageBuilder:
    """This class handles constructing the PR messages to be sent."""

    def make_message(self, pr_data: PrData) -> str:
        """
        This method checks the pr data and makes a string message from it.
        :param pr_data: The PR info
        :return: The message to post
        """
        checked_info = self.add_user_info_and_age(pr_data)
        return self._construct_string(checked_info)

    @staticmethod
    def _construct_string(pr_data: PrData) -> str:
        """
        This method constructs the PR message.
        :param pr_data: The data class containing the info about the PR.
        :return: The message as a single string.
        """
        client = WebClient(token=get_token("SLACK_BOT_TOKEN"))
        try:
            name = client.users_profile_get(user=pr_data.user)["profile"]["real_name"]
        except SlackApiError:
            name = pr_data.user

        message = []
        if pr_data.old:
            message.append("*This PR is older than 90 days. Consider closing it:*")
        message.append(f"Pull Request: <{pr_data.url}|{pr_data.pr_title}>")
        message.append(f"Author: {name}")
        return "\n".join(message)

    @staticmethod
    def _check_pr_age(time_created: datetime) -> bool:
        """
        This method checks if the PR is older than 3 months.
        :param time_created: The date the PR was created.
        :return: PR older or not.
        """
        opened_date = time_created.replace(tzinfo=None)
        datetime_now = datetime.now().replace(tzinfo=None)
        time_cutoff = datetime_now - timedelta(days=30)
        return opened_date < time_cutoff

    def add_user_info_and_age(self, info: PrData) -> PrData:
        """
        This method validates certain information in the PR data such as who authored the PR and if it's old or not.
        :param info: The information to validate.
        :return: The validated information.
        """
        slack_ids = get_config("user-map")
        new_info = replace(
            info,
            user=slack_ids.get(info.user, info.user),
            old=self._check_pr_age(info.created_at),
        )
        return new_info
