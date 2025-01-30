"""This module stores slash command functions. This is to reduce the code in the main and dev modules."""

import os
from helper.data import filter_by
from helper.read_config import get_config, get_token
from find_pr_api.github import FindPRs as FindPRsGitHub
from find_pr_api.gitlab import FindPRs as FindPRsGitLab
from slack_reminder_api.pr_reminder import send_reminders


def slash_prs(ack, respond, command):
    """
    This event sends a message to the user containing open PRs.
    :param command: The return object from Slack API.
    :param ack: Slacks acknowledgement command.
    :param respond: Slacks respond command to respond to the command in chat.
    """
    ack()
    users = get_config("users")
    if command["user_id"] not in [user.slack_id for user in users]:
        respond(
            f"Could not find your Slack ID {command["user_id"]} in the user map. "
            f"Please contact the service maintainer to fix this."
        )
        return

    if command["text"] != "mine" and command["text"] != "all":
        respond("Please provide the correct argument: 'mine' or 'all'.")
        return

    user = filter_by(users, "slack_id", command["user_id"])[0]

    respond("Finding the PRs...")
    prs = FindPRsGitHub().run(
        repos=get_config("repos"), token=get_token("GITHUB_TOKEN")
    )

    if command["text"] == "mine":
        prs = filter_by(obj_list=prs, prop="author", value=user.github_name)
        send_reminders(user.slack_id, prs, True)

    elif command["text"] == "all":
        send_reminders(user.slack_id, prs, True)


def slash_mrs(ack, respond, command):
    """
    This event sends a message to the user containing open MRs.
    :param command: The return object from Slack API.
    :param ack: Slacks acknowledgement command.
    :param respond: Slacks respond command to respond to the command in chat.
    """
    ack()
    users = get_config("users")
    if command["user_id"] not in [user.slack_id for user in users]:
        respond(
            f"Could not find your Slack ID {command["user_id"]} in the user map. "
            f"Please contact the service maintainer to fix this."
        )
        return

    if command["text"] != "mine" and command["text"] != "all":
        respond("Please provide the correct argument: 'mine' or 'all'.")
        return

    user = filter_by(users, "slack_id", command["user_id"])[0]

    respond("Finding the MRs...")
    prs = FindPRsGitLab().run(
        projects=get_config("projects"), token=get_token("GITLAB_TOKEN")
    )

    if command["text"] == "mine":
        prs = filter_by(obj_list=prs, prop="author", value=user.gitlab_name)
        send_reminders(user.slack_id, prs, True)

    elif command["text"] == "all":
        send_reminders(user.slack_id, prs, True)
