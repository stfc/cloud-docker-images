"""
This module uses endpoints to run the Slack app.
It listens for requests from Slack and executes different functions.
"""

import logging

from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from flask import Flask, request


from helper.read_config import get_token, validate_required_files
from events.weekly_reminders import weekly_reminder
from events.slash_commands import slash_prs, slash_mrs


logging.basicConfig(level=logging.DEBUG)

validate_required_files()

slack_app = App(
    token=get_token("SLACK_BOT_TOKEN"), signing_secret=get_token("SLACK_SIGNING_SECRET")
)


@slack_app.event("message")
def handle_message_events(body, logger):
    """This method handles message events and logs them."""
    logger.info(body)


@slack_app.command("/prs")
def prs(ack, respond, command):
    """See events/slash_commands.py for documentation."""
    slash_prs(ack, respond, command)


@slack_app.command("/mrs")
def prs(ack, respond, command):
    """See events/slash_commands.py for documentation."""
    slash_mrs(ack, respond, command)


flask_app = Flask(__name__)
slack_handler = SlackRequestHandler(slack_app)


@flask_app.route("/slack/events", methods=["POST"])
def slack_events() -> slack_handler.handle:
    """This function makes requests to the Slack App from the Flask request."""
    return slack_handler.handle(request)


@flask_app.route("/slack/schedule", methods=["POST"])
def slack_schedule() -> str:
    """This function checks the request is authorised then passes it to the weekly reminder calls."""
    token = request.headers.get("Authorization")
    if token != get_token("SCHEDULED_REMINDER_TOKEN"):
        return "403"
    weekly_reminder(request.json)
    return "200"


if __name__ == "__main__":
    from waitress import serve

    serve(flask_app, host="0.0.0.0", port=3000)
