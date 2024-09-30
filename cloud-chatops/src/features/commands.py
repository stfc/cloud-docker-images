"""This module handles the posting of messages to Slack using the Slack SDK WebClient class."""

from typing import List
from enum_states import PRsFoundState
from features.base_feature import BaseFeature, PRMessageBuilder
from pr_dataclass import PrData


class PostToDMs(BaseFeature):
    """
    This class handles the Slack posting.
    """

    # pylint: disable=R0903
    # Each feature should have only one entry point called run
    def __init__(self):
        super().__init__()
        self.thread_ts = None
        self.user = None
        self.message_builder = PRMessageBuilder()

    def run(self, channel: str, post_all: bool) -> None:
        """
        This method calls the functions to post the reminder message and further PR messages.
        :param channel: The users channel ID to post to.
        :param post_all: To post all PRs found or only ones authored by the user.
        """
        self.channel = channel
        self.user = channel
        self.prs = self._format_prs(self.prs)
        reminder_thread_ts = self._post_reminder_message()
        self._post_thread_messages(self.prs, reminder_thread_ts, post_all)

    def _post_thread_messages(
        self, prs: List[PrData], thread_ts: str, post_all: bool
    ) -> None:
        """
        This method iterates through each PR and calls the post method for them.
        :param post_all: To post all prs or user only prs.
        :param thread_ts: Timestamp of reminder message
        :param prs: A list of PRs from GitHub
        """
        prs_posted = PRsFoundState.NONE_FOUND
        for pr in prs:
            post_status = self._filter_thread_message(pr, thread_ts, post_all)
            if post_status == PRsFoundState.PRS_FOUND:
                prs_posted = PRsFoundState.PRS_FOUND

        if prs_posted == PRsFoundState.NONE_FOUND:
            self._send_no_prs_found(thread_ts)

    def _filter_thread_message(
        self, pr: PrData, thread_ts: str, post_all: bool
    ) -> PRsFoundState:
        """
        This method filters which pull requests to send to the thread dependent on the value of personal_thread.
        If personal_thread holds a value, only PRs authored by that user will be sent to the thread.
        Else, all the PRs will be sent.
        :param post_all: To post all PRs or user specific PRs
        :param pr: The PR info to send in a message.
        :param thread_ts: Timestamp of reminder message
        :return: Returns an Enum state.
        """
        if post_all or (not post_all and pr.user == self.user):
            response = self._send_thread(pr, thread_ts)
            self._send_thread_react(pr, response.data["channel"], response.data["ts"])
            return PRsFoundState.PRS_FOUND

        return PRsFoundState.NONE_FOUND
