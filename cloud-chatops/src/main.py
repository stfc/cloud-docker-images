"""
This module starts the Slack Bolt app Asynchronously running the event loop.
Using Socket mode, the app listens for events from the Slack API client.
"""

import logging
import asyncio
from slack_bolt.app.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler
from helper.read_config import get_token, validate_required_files
from events import slash_prs, schedule_jobs, slash_find_host


logging.basicConfig(level=logging.DEBUG)
app = AsyncApp(token=get_token("SLACK_BOT_TOKEN"))


@app.event("message")
async def handle_message_events(body, logger):
    """This method handles message events and logs them."""
    logger.info(body)


@app.command("/prs")
async def prs(ack, respond, command):
    """
    This command sends the user a message containing all open pull requests.
    :param command: The return object from Slack API.
    :param ack: Slacks acknowledgement command.
    :param respond: Slacks respond command to respond to the command in chat.
    """
    await slash_prs(ack, respond, command)


@app.command("/find-host")
async def find_host(ack, respond):
    """
    This command responds to the user with the IP of the host that received the message.
    :param ack: Slacks acknowledgement command.
    :param respond: Slacks respond command to respond to the command in chat.
    """
    await slash_find_host(ack, respond)


async def entrypoint() -> None:
    """
    This function is the main entry point for the app. First, it validates the required files.
    Then it starts the async loop and runs the scheduler.
    """
    validate_required_files()
    asyncio.ensure_future(schedule_jobs())
    handler = AsyncSocketModeHandler(app, get_token("SLACK_APP_TOKEN"))
    await handler.start_async()


def main():
    """This method is the entry point if using this package."""
    asyncio.run(entrypoint())


if __name__ == "__main__":
    asyncio.run(entrypoint())
