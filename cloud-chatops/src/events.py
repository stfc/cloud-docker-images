"""
This module contains events to run in main.py.
"""

import asyncio
import schedule
from features.pr_reminder import PostPRsToSlack
from features.post_to_dms import PostToDMs
from read_data import get_config

PULL_REQUESTS_CHANNEL = "C03RT2F6WHZ"


def run_global_reminder(channel) -> None:
    """This event sends a message to the specified channel with all open PRs."""
    PostPRsToSlack().run(channel=channel)


def run_personal_reminder() -> None:
    """This event sends a message to each user in the user map with their open PRs."""
    users = list(get_config("user-map").values())
    PostToDMs().run(users=users, post_all=False)


async def schedule_jobs() -> None:
    """
    This function schedules tasks for the async loop to run.
    """

    schedule.every().monday.at("09:00").do(
        run_global_reminder, channel=PULL_REQUESTS_CHANNEL
    )

    schedule.every().wednesday.at("09:00").do(
        run_global_reminder, channel=PULL_REQUESTS_CHANNEL
    )

    schedule.every().monday.at("09:00").do(run_personal_reminder)

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
    if command["text"] == "mine":
        await respond("Gathering the PRs...")
        PostToDMs().run([user_id], False)
    elif command["text"] == "all":
        await respond("Gathering the PRs...")
        PostToDMs().run([user_id], True)
    else:
        await respond("Please provide the correct argument: 'mine' or 'all'.")
        return

    await respond("Check out your DMs.")
