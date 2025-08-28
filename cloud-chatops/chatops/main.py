"""
Initialise the app.
Set up logging and define routes and events.
"""

import os
import logging
from typing import Tuple

from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
import waitress
from flask import Flask, request, make_response
from helper.validate_config import validate_required_files
from helper import config as app_config
from events.weekly_reminders import weekly_reminder
from events.slash_prs import SlashPRs


def configure_logging():
    """
    Configure logging for Flask, Waitress and Slack Bolt to output to stdout.
    """
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
    )
    log_level = getattr(logging, os.environ.get("LOGLEVEL", "INFO").upper())

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)

    logging.getLogger("waitress").setLevel(log_level)
    logging.getLogger("slack_bolt").setLevel(log_level)
    logging.getLogger("flask_app").setLevel(log_level)


configure_logging()
config = app_config.load_config()
secrets = app_config.load_secrets()

validate_required_files()

slack_app = App(
    token=secrets.SLACK_BOT_TOKEN, signing_secret=secrets.SLACK_SIGNING_SECRET
)


@slack_app.event("message")
def handle_message_events(body, logger):
    """
    This method handles message events and logs them.
    """
    logger.info(body)

@slack_app.command("/prs")
def prs(ack, respond, body, logger):
    """
    See :py:func: `~chatops.events.SlashPRs.run`
    """
    logger.info(body)
    SlashPRs().run(ack, respond, body)


flask_app = Flask(__name__)
slack_handler = SlackRequestHandler(slack_app)


@flask_app.route("/slack/events", methods=["POST"])
def slack_events() -> slack_handler.handle:
    """
    Take Slack Events from the Flask app and give them to the Slack Handler to handle them.
    """
    return slack_handler.handle(request)


@flask_app.route("/slack/schedule", methods=["POST"])
def slack_schedule() -> Tuple[str, int]:
    """
    Provides a route to trigger weekly Slack reminders.
    Authenticates the request based on token provided.
    """
    flask_app.logger.info(request.json)
    token = request.headers.get("Authorization")
    if token != "token " + secrets.SCHEDULED_REMINDER_TOKEN:
        flask_app.logger.info(
            "Request on /slack/schedule by %s provided an invalid token.",
            request.remote_addr,
        )
        return (
            "Invalid token provided. Please make sure your token is in the format 'token gh_abc123...'",
            403,
        )
    weekly_reminder(request.json)
    flask_app.logger.info(
        "Request on /slack/schedule by %s executed successfully "
        "for reminder type %s.",
        request.remote_addr,
        request.json["reminder_type"],
    )
    return "OK", 200


@flask_app.route("/health", methods=["GET"])
def health_check():
    """Provides an endpoint to check the health of the API."""
    flask_app.logger.info("Health check called.")
    response = make_response()
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = "0"
    response.status = 200
    return response


if __name__ == "__main__":
    waitress.serve(flask_app, host="0.0.0.0", port=3000)
