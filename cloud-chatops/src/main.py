"""
This module starts the Slack Bolt application Asynchronously running the event loop.
Using Socket mode, the application listens for events from the Slack API client.
"""

import logging
import asyncio
from slack_bolt.app.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler
import schedule
from features.pr_reminder import PostPRsToSlack
from features.commands import PostToDMs
from read_data import get_token, validate_required_files


logging.basicConfig(level=logging.DEBUG)
app = AsyncApp(token=get_token("SLACK_BOT_TOKEN"))


@app.event("message")
async def handle_message_events(body, logger):
    """This method handles message events and logs them."""
    logger.info(body)


@app.command("/prs")
async def remind_prs(ack, respond, command):
    """
    This function calls the messaging method to notify a user about their open PRs or all open PRs if asked.
    :param command: The return object from Slack API.
    :param ack: Slacks acknowledgement command.
    :param respond: Slacks respond command to respond to the command in chat.
    """
    await ack()
    channel = command["user_id"]
    if command["text"] == "mine":
        await respond("Gathering the PRs...")
        PostToDMs().run(channel, False)
    elif command["text"] == "all":
        await respond("Gathering the PRs...")
        PostToDMs().run(channel, True)
    else:
        await respond("Please provide the correct argument: 'mine' or 'all'.")
        return

    await respond("Check out your DMs.")


async def schedule_jobs() -> None:
    """
    This function schedules tasks for the async loop to run.
    """

    def run_pr(channel, mention=False) -> None:
        """
        This is a placeholder function for the schedule to accept.
        """
        PostPRsToSlack(mention=mention).run(channel=channel)

    schedule.every().monday.at("09:00").do(
        run_pr, mention=True, channel="pull-requests"
    )

    while True:
        schedule.run_pending()
        await asyncio.sleep(10)


async def run_app() -> None:
    """
    This function is the main entry point for the application. First, it validates the required files.
    Then it starts the async loop and runs the scheduler.
    """
    validate_required_files()
    asyncio.ensure_future(schedule_jobs())
    handler = AsyncSocketModeHandler(app, get_token("SLACK_APP_TOKEN"))
    await handler.start_async()


def main():
    """This method is the entry point if using this package."""
    asyncio.run(run_app())


if __name__ == "__main__":
    asyncio.run(run_app())
