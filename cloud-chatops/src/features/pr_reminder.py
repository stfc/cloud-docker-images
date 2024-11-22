"""This module sends reminders to direct messages and channels with open pull requests."""

from dataclasses import replace
from typing import List, Tuple, Union
from datetime import datetime
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from pr_dataclass import PR, PRProps, Message
from read_data import get_config


class PRReminder:
    """This class sends reminders about pull requests to channels."""

    def __init__(self, client: WebClient):
        self.client = client

    def run(
        self,
        prs: List[PR],
        channel: str,
        filter_by: Tuple[PRProps, Union[str, datetime, bool]] = None,
        message_no_prs: bool = True,
    ) -> None:
        """
        Send pull request reminders to a channel.
        :param prs: List of pull requests.
        :param channel: The channel to send reminders to. This can be a public channel or a user ID.
        :param filter_by: Property to filter pull requests by.
        :param message_no_prs: Send a message that there are no PRs.
        """
        if filter_by:
            prs = list(
                filter(
                    lambda pr: getattr(pr, str(filter_by[0]).split(sep=".")[1].lower())
                    == filter_by[1],
                    prs,
                )
            )

        if not prs and message_no_prs:
            self.send_message(text="No Pull Requests were found.", channel=channel)
            return

        if not prs and not message_no_prs:
            return

        messages = self.construct_messages(prs)

        reminder_message = self.send_message(
            text="Here are the outstanding PRs as of today:", channel=channel
        )

        for message in messages:
            self.send_message(
                text=message.text,
                channel=channel,
                reactions=message.reactions,
                timestamp=reminder_message.data["ts"],
            )

    def send_message(
        self,
        text: str,
        channel: str,
        reactions: List[str] = None,
        timestamp: str = None,
    ) -> WebClient.chat_postMessage:
        """
        Send a message using the Slack Client.
        :param text: Text to send in the message
        :param channel: Channel to send the message to
        :param reactions: Reactions to react with.
        :param timestamp: Timestamp of thread to send the message in.
        :return: Slack API response object
        """
        kwargs = {"text": text, "channel": channel, "unfurl_links": False}
        if timestamp:
            kwargs["thread_ts"] = timestamp
        response = self.client.chat_postMessage(**kwargs)

        if not response["ok"]:
            raise RuntimeError(
                f'Message failed to send with error: {response["error"]}'
            )

        if reactions:
            self.add_reactions(response.data["ts"], channel, reactions)

        return response

    def add_reactions(self, timestamp: str, channel: str, reactions: List[str]) -> None:
        """
        Add reactions to messages.
        :param timestamp: Timestamp of the message.
        :param channel: Channel the message was sent to.
        :param reactions: Reactions to add.
        """
        for react in reactions:
            response = self.client.reactions_add(
                channel=channel, name=react, timestamp=timestamp
            )
            if not response["ok"]:
                raise RuntimeError(
                    f'Reaction failed to add with error: {response["error"]}'
                )

    def construct_messages(self, prs: List[PR]) -> List[Message]:
        """
        Constructs string messages and extracts needed reactions from the dataclass.
        :param prs: List of pull requests to create messages from.
        :return: List of message data ready to send
        """
        messages = []
        for pr in prs:
            string = self.make_string(pr)
            reactions = self.get_reactions(pr)
            messages.append(Message(text=string, reactions=reactions))
        return messages

    def make_string(self, pr: PR) -> str:
        """
        Creates string from PR data.
        :param pr: PR data
        :return: String message
        """
        slack_ids = get_config("user-map")
        pr = replace(pr, author=slack_ids.get(pr.author, pr.author))
        try:
            name = self.client.users_profile_get(user=pr.author)["profile"]["real_name"]
        except SlackApiError:
            name = pr.author
        message = []
        if pr.stale:
            message.append("*This PR is older than 30 days. Consider closing it:*")
        message.append(f"Pull Request: <{pr.url}|{pr.title}>")
        message.append(f"Author: {name}")
        return "\n".join(message)

    @staticmethod
    def get_reactions(pr: PR) -> List[str]:
        """
        Returns all needed reactions
        :param pr: PR data
        :return: Reactions
        """
        reactions = []
        if pr.stale:
            reactions.append("alarm_clock")
        if pr.draft:
            reactions.append("building_construction")
        return reactions
