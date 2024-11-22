"""
This module contains events to run in main.py.
"""

from typing import List
import asyncio
from slack_sdk import WebClient
import schedule
from features.pr_reminder import PRReminder
from find_prs import FindPRs
from read_data import get_config, get_token
from pr_dataclass import PRProps

PULL_REQUESTS_CHANNEL = "C03RT2F6WHZ"


def run_global_reminder(channel) -> None:
    """This event sends a message to the specified channel with all open PRs."""
    prs = FindPRs().run(repos=get_config("repos"), sort=(PRProps.CREATED_AT, False))
    PRReminder(WebClient(token=get_token("SLACK_BOT_TOKEN"))).run(
        prs=prs,
        channel=channel,
    )


def run_personal_reminder(users: List[str]) -> None:
    """
    This event sends a message to each user in the user map with their open PRs.
    :param users: Users to send reminders to.
    """
    prs = FindPRs().run(repos=get_config("repos"), sort=(PRProps.CREATED_AT, False))
    client = WebClient(token=get_token("SLACK_BOT_TOKEN"))
    user_map = get_config("user-map")
    for user in users:
        github_user = list(user_map.keys())[list(user_map.values()).index(user)]
        PRReminder(client).run(
            prs=prs,
            channel=user,
            filter_by=(PRProps.AUTHOR, github_user),
            message_no_prs=False,
        )


async def schedule_jobs() -> None:
    """
    This function schedules tasks for the async loop to run.
    These dates and times are hardcoded for production use.
    """

    schedule.every().monday.at("09:00").do(
        run_global_reminder, channel=PULL_REQUESTS_CHANNEL
    )

    schedule.every().wednesday.at("09:00").do(
        run_global_reminder, channel=PULL_REQUESTS_CHANNEL
    )

    schedule.every().monday.at("09:00").do(
        run_personal_reminder, users=list(get_config("user-map").values())
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

    if user_id not in get_config("user-map").values():
        await respond(
            f"Could not find your Slack ID {user_id} in the user map. "
            f"Please contact the service maintainer to fix this."
        )
        return

    if command["text"] == "mine":
        await respond("Gathering the PRs...")
        run_personal_reminder([user_id])
    elif command["text"] == "all":
        await respond("Gathering the PRs...")
        run_global_reminder(user_id)
    else:
        await respond("Please provide the correct argument: 'mine' or 'all'.")
        return

    await respond("Check out your DMs.")
