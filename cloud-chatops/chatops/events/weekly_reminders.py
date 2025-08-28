"""This module contains the weekly reminder functions."""

from typing import List, Dict
from slack_sdk import WebClient
from helper.data import User, sort_by, filter_by
from helper.config import get_config, get_secrets
from notify.slack import PRReminder
from find_pr.github import GitHub as FindPRsGitHub
from find_pr.gitlab import GitLab as FindPRsGitLab


def run_global_reminder(channel: str) -> None:
    """
    This event sends a message to the specified channel with all open PRs.
    :param channel: Channel ID to send the messages to.
    """
    config = get_config()
    secrets = get_secrets()
    unsorted_prs = []
    if config.github.enabled:
        unsorted_prs += FindPRsGitHub().run(
            repos=config.github.repositories, token=secrets.GITHUB_TOKEN
        )
    if config.gitlab.enabled:
        unsorted_prs += FindPRsGitLab().run(
            projects=config.gitlab.projects, token=secrets.GITLAB_TOKEN
        )

    prs = sort_by(unsorted_prs, "created_at", False)
    PRReminder(WebClient(token=secrets.SLACK_BOT_TOKEN)).run(
        prs=prs,
        channel=channel,
    )


def run_personal_reminder(users: List[User], message_no_prs: bool = False) -> None:
    """
    This event sends a message to each user in the user map with their open PRs.
    :param message_no_prs: Send a message saying there are no PRs open.
    :param users: Users to send reminders to.
    """
    config = get_config()
    secrets = get_secrets()
    unsorted_prs = []
    if config.github.enabled:
        unsorted_prs += FindPRsGitHub().run(
            repos=config.github.repositories, token=secrets.GITHUB_TOKEN
        )
    if config.gitlab.enabled:
        unsorted_prs += FindPRsGitLab().run(
            projects=config.gitlab.projects, token=secrets.GITLAB_TOKEN
        )

    prs = sort_by(unsorted_prs, "created_at", False)
    client = WebClient(token=secrets.SLACK_BOT_TOKEN)
    for user in users:
        filtered_prs = filter_by(prs, "author", [user.github_name, user.gitlab_name])
        PRReminder(client).run(
            prs=filtered_prs,
            channel=user.slack_id,
            message_no_prs=message_no_prs,
        )


def weekly_reminder(message_data: Dict) -> None:
    """
    This function chooses which type of reminder to call based on its arguments.
    :param message_data: Data from the POST request.
    """
    config = get_config()
    reminder_type = message_data["reminder_type"]
    channel = message_data.get("channel", "")
    if reminder_type == "global":
        if not channel:
            raise ValueError(
                "Channel not provided in POST message. Cannot complete request."
            )
        run_global_reminder(channel)
    elif reminder_type == "personal":
        run_personal_reminder(users=config.users, message_no_prs=False)
    else:
        raise ValueError(
            f'Reminder type {reminder_type} is not supported. Use either "global" or "personal".'
        )
