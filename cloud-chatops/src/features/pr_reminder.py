"""This module handles the posting of messages to Slack using the Slack SDK WebClient class."""

from typing import List
from datetime import datetime, timedelta
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from read_data import get_token, get_user_map, get_repos
from get_github_prs import GetGitHubPRs
from pr_dataclass import PrData
from custom_exceptions import ChannelNotFound

DEFAULT_CHANNEL = "C06U37Y02R4"  # STFC-cloud: dev-chatops
# If the PR author is not in the Slack ID mapping
# then we set the user to mention as David Fairbrother
# as the team lead to deal with this PR.
DEFAULT_AUTHOR = "U01JG0LKU3W"


class PostPRsToSlack:
    # pylint: disable=R0903
    # Disabling this as there only needs to be one entry point.
    """
    This class handles the Slack posting.
    """

    def __init__(self, mention=False):
        self.channel = DEFAULT_CHANNEL
        self.thread_ts = ""
        self.mention = mention
        self.slack_ids = get_user_map()
        self.message_builder = PRMessageBuilder(self.mention)
        self.client = WebClient(token=get_token("SLACK_BOT_TOKEN"))
        self.prs = GetGitHubPRs(get_repos(), "stfc").run()

    def run(self, channel=None) -> None:
        """
        This method sets class attributes then cals the reminder and thread post methods.
        :param channel: Changes the channel to post the messages to.
        """
        if channel:
            self._set_channel_id(channel)

        self._post_reminder_message()
        self._post_thread_messages(self.prs)

    def _post_reminder_message(self) -> None:
        """
        This method posts the main reminder message to start the thread if PR notifications.
        """
        response = self.client.chat_postMessage(
            channel=self.channel,
            text="Here are the outstanding PRs as of today:",
        )
        self.thread_ts = response.data["ts"]

    def _post_thread_messages(self, prs: List[PrData]) -> None:
        """
        This method iterates through each PR and calls the post method for them.
        :param prs: A list of PRs from GitHub
        """
        prs_found = False
        for pr in prs:
            prs_found = True
            response = self._send_thread(pr)
            self._send_thread_react(pr, response.data["ts"])

        if not prs_found:
            self._send_no_prs_found()

    def _send_thread(self, pr_data: PrData) -> WebClient.chat_postMessage:
        """
        This method sends the message and returns the response.
        :param pr_data: The PR data as a dataclass
        :return: The message response.
        """
        message = self.message_builder.make_message(pr_data)
        response = self.client.chat_postMessage(
            text=message,
            channel=self.channel,
            thread_ts=self.thread_ts,
            unfurl_links=False,
        )
        assert response["ok"]
        return response

    def _send_thread_react(self, pr_data: PrData, message_ts: str) -> None:
        """
        This method sends reactions to the PR message if necessary.
        :param pr_data: The PR info
        :param message_ts: The timestamp of the message to react to
        """
        reactions = {
            "old": "alarm_clock",
            "draft": "scroll",
        }
        for react, react_id in reactions.items():
            if getattr(pr_data, react):
                react_response = self.client.reactions_add(
                    channel=self.channel, name=react_id, timestamp=message_ts
                )
                assert react_response["ok"]

    def _send_no_prs_found(self) -> None:
        """
        This method sends a message to the chat that there are no PRs.
        """
        self.client.chat_postMessage(
            text="There are no outstanding pull requests open.",
            channel=self.channel,
            thread_ts=self.thread_ts,
            unfurl_links=False,
        )

    def _set_channel_id(self, channel_name: str) -> None:
        """
        This method will get the channel id from the channel name and set the attrribute to the class.
        This is necessary as the chat.postMessage method takes name or id but reactions.add only takes id.
        This method also acts as a channel verif
        :param channel_name: The channel name to lookup
        :return:
        """
        channels = self.client.conversations_list(types="private_channel")["channels"]
        channel_obj = next(
            (channel for channel in channels if channel["name"] == channel_name), None
        )
        if channel_obj:
            self.channel = channel_obj["id"]
        else:
            raise ChannelNotFound(
                f"The channel {channel_name} could not be found. Check the bot is a member of the channel.\n"
                f' You can use "/invite @Cloud ChatOps" to invite the app to your channel.'
            )


class PRMessageBuilder:
    """This class handles constructing the PR messages to be sent."""

    # pylint: disable=R0903
    # Disabling this as there only needs to be one entry point.
    def __init__(self, mention):
        self.client = WebClient(token=get_token("SLACK_BOT_TOKEN"))
        self.slack_ids = get_user_map()
        self.mention = mention

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
        if self.mention and not pr_data.draft:
            message.append(f"Author: <@{pr_data.user}>")
        else:
            name = self._get_real_name(pr_data.user)
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
        if user not in self.slack_ids:
            user = DEFAULT_AUTHOR
        else:
            user = self.slack_ids[user]
        return user

    @staticmethod
    def _check_pr_age(time_created: str) -> bool:
        """
        This method checks if the PR is older than 6 months.
        :param time_created: The date the PR was created.
        :return: PR older or not.
        """
        opened_date = datetime.fromisoformat(time_created).replace(tzinfo=None)
        datetime_now = datetime.now().replace(tzinfo=None)
        time_cutoff = datetime_now - timedelta(days=30 * 6)
        return opened_date < time_cutoff

    def _check_pr_info(self, info: PrData) -> PrData:
        """
        This method validates certain information in the PR data such as who authored the PR and if it's old or not.
        :param info: The information to validate.
        :return: The validated information.
        """
        info.user = self._github_to_slack_username(info.user)
        info.old = self._check_pr_age(info.created_at)
        return info
