"""
This module starts the Slack Bolt app Asynchronously running the event loop.
Using Socket mode, the app listens for events from the Slack API client.
"""

import logging
import os

from slack_bolt import App

from helper.read_config import get_token, validate_required_files
from events import slash_prs, slash_find_host


logging.basicConfig(level=logging.DEBUG)
app = App(token=get_token("SLACK_BOT_TOKEN"), signing_secret=get_token("SLACK_SIGNING_SECRET"))


@app.event("message")
def handle_message_events(body, logger):
    """This method handles message events and logs them."""
    logger.info(body)


@app.command("/prs")
def prs(ack, respond, command):
    """
    This command sends the user a message containing all open pull requests.
    :param command: The return object from Slack API.
    :param ack: Slacks acknowledgement command.
    :param respond: Slacks respond command to respond to the command in chat.
    """
    slash_prs(ack, respond, command)


@app.command("/find-host")
def find_host(ack, respond):
    """
    This command responds to the user with the IP of the host that received the message.
    :param ack: Slacks acknowledgement command.
    :param respond: Slacks respond command to respond to the command in chat.
    """
    slash_find_host(ack, respond)


if __name__ == "__main__":
    validate_required_files()
    app.start(port=int(os.environ.get("PORT", 3000)))
