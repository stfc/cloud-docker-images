import os
from helper.data import filter_by
from helper.read_config import get_config, get_token
from find_pr_api.github import FindPRs as FindPRsGitHub
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
    prs = FindPRsGitHub().run(repos=get_config("repos"), token=get_token("GITHUB_TOKEN"))

    if command["text"] == "mine":
        prs = filter_by(obj_list=prs, prop="author", value=user.github_name)
        send_reminders(user.slack_id, prs, True)

    elif command["text"] == "all":
        send_reminders(user.slack_id, prs, True)


def slash_find_host(ack, respond):
    """
    Responds to the user with the host IP of the machine that received the command.
    :param ack: Slacks acknowledgement command.
    :param respond: Slacks respond command to respond to the command in chat.
    """
    ack()
    host_ip = os.environ.get("HOST_IP")
    respond(f"The host IP of this node is: {host_ip}")