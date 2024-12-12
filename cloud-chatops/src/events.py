"""
This module contains events to run in main.py.
"""

import os
from typing import List
import asyncio
from slack_sdk import WebClient
import schedule

from data import User
from features.pr_reminder import PRReminder
from find_prs import FindPRs
from read_data import get_config, get_token


def run_global_reminder(channel: str) -> None:
    """This event sends a message to the specified channel with all open PRs."""
    unsorted_prs = FindPRs().run(repos=get_config("repos"))
    prs = FindPRs().sort_by(unsorted_prs, "created_at", False)
    PRReminder(WebClient(token=get_token("SLACK_BOT_TOKEN"))).run(
        prs=prs,
        channel=channel,
    )


def run_personal_reminder(users: List[User], message_no_prs: bool = False) -> None:
    """
    This event sends a message to each user in the user map with their open PRs.
    :param message_no_prs: Send a message saying there are no PRs open.
    :param users: Users to send reminders to.
    """
    unsorted_prs = FindPRs().run(repos=get_config("repos"))
    prs = FindPRs().sort_by(unsorted_prs, "created_at", False)
    client = WebClient(token=get_token("SLACK_BOT_TOKEN"))
    for user in users:
        filtered_prs = FindPRs().filter_by(prs, "author", user.github_name)
        PRReminder(client).run(
            prs=filtered_prs,
            channel=user.slack_id,
            message_no_prs=message_no_prs,
        )


async def schedule_jobs() -> None:
    """
    This function schedules tasks for the async loop to run.
    These dates and times are hardcoded for production use.
    """
    channel = get_config("channel")

    schedule.every().monday.at("09:00").do(run_global_reminder, channel=channel)

    schedule.every().wednesday.at("09:00").do(run_global_reminder, channel=channel)

    schedule.every().monday.at("09:00").do(
        run_personal_reminder, users=get_config("users")
    )

    while True:
        schedule.run_pending()
        await asyncio.sleep(10)


async def slash_prs(ack, respond, command):
    """
    This event sends a message to the user containing open PRs.
    :param command: The return object from Slack API.
    :param ack: Slacks acknowledgement command.
    :param respond: Slacks respond command to respond to the command in chat.
    """
    await ack()
    user_id = command["user_id"]
    users = get_config("users")
    if user_id not in [user.slack_id for user in users]:
        await respond(
            f"Could not find your Slack ID {user_id} in the user map. "
            f"Please contact the service maintainer to fix this."
        )
        return

    if command["text"] == "mine":
        await respond("Gathering the PRs...")
        run_personal_reminder(
            [user for user in users if user.slack_id == user_id], message_no_prs=True
        )
    elif command["text"] == "all":
        await respond("Gathering the PRs...")
        run_global_reminder(user_id)
    else:
        await respond("Please provide the correct argument: 'mine' or 'all'.")
        return

    await respond("Check out your DMs.")


async def slash_find_host(ack, respond):
    """
    Responds to the user with the host IP of the machine that received the command.
    :param ack: Slacks acknowledgement command.
    :param respond: Slacks respond command to respond to the command in chat.
    """
    await ack()
    host_ip = os.environ.get("HOST_IP")
    await respond(f"The host IP of this node is: {host_ip}")
