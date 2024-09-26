"""This module handles the posting of messages to Slack using the Slack SDK WebClient class."""

from typing import List
from enum_states import PRsFoundState
from features.base_feature import BaseFeature, PRMessageBuilder
from pr_dataclass import PrData


class PostPRsToSlack(BaseFeature):
    # pylint: disable=R0903
    # Disabling this as there only needs to be one entry point.
    """
    This class handles the Slack posting.
    """

    def __init__(self):
        super().__init__()
        self.message_builder = PRMessageBuilder()

    def run(self, channel=None) -> None:
        """
        This method sets class attributes then cals the reminder and thread post methods.
        :param channel: Changes the channel to post the messages to.
        """
        if channel:
            self.channel = channel

        reminder_thread_ts = self._post_reminder_message()
        self._post_thread_messages(self.prs, reminder_thread_ts)

    def _post_thread_messages(self, prs: List[PrData], thread_ts: str) -> None:
        """
        This method iterates through each PR and calls the post method for them.
        :param prs: A list of PRs from GitHub
        :param thread_ts: Timestamp of reminder message
        """
        prs_found = PRsFoundState.NONE_FOUND
        for pr in prs:
            prs_found = PRsFoundState.PRS_FOUND
            response = self._send_thread(pr, thread_ts)
            self._send_thread_react(pr, response.data["channel"], response.data["ts"])

        if not prs_found:
            self._send_no_prs_found(thread_ts)
