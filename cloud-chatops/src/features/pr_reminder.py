"""This module posts a PR reminder message to the pull-requests channel."""

from typing import List
from features.base_feature import BaseFeature
from pr_dataclass import PR


class PostPRsToSlack(BaseFeature):
    # pylint: disable=R0903
    # Each feature should have only one entry point called run
    """
    This class handles the Slack posting.
    """

    def run(self, channel=None) -> None:
        """
        This method sets class attributes then cals the reminder and thread post methods.
        :param channel: Changes the channel to post the messages to.
        """
        if channel:
            self.channel = channel

        reminder_thread_ts = self._post_reminder_message()
        self._post_thread_messages(self.prs, reminder_thread_ts)

    def _post_thread_messages(self, prs: List[PR], thread_ts: str) -> None:
        """
        This method iterates through each PR and calls the post method for them.
        :param prs: A list of PRs from GitHub
        :param thread_ts: Timestamp of reminder message
        """
        if not prs:
            self._send_no_prs_found(thread_ts)

        for pr in prs:
            response = self._send_thread(pr, thread_ts)
            self._send_thread_react(pr, response.data["channel"], response.data["ts"])
