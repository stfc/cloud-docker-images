"""This module contains code for the Slack command /prs."""

from typing import List
from helper.data import filter_by, User
from helper.read_config import get_config, get_token
from find_pr_api.github import GitHub as FindPRsGitHub
from find_pr_api.gitlab import GitLab as FindPRsGitLab
from slack_reminder_api.pr_reminder import send_reminders


# pylint: disable = R0903
class SlashPRs:
    """Class triggered by the Slack command /prs."""

    def run(self, ack, respond, body) -> None:
        """
        This event sends a message to the user containing open PRs.
        :param body: The return data from the API.
        :param ack: Slacks acknowledgement command.
        :param respond: Slacks respond command to respond to the command in chat.
        """
        ack()
        users = get_config("users")

        self._check_if_features_enabled(respond)
        self._check_user_exists(body["user_id"], users, respond)
        self._check_correct_arguments(body["text"], respond)

        user = filter_by(users, "slack_id", [body["user_id"]])[0]

        respond("Finding the PRs...")
        prs = []
        if get_config("github")["enabled"]:
            prs.extend(
                FindPRsGitHub().run(
                    repos=get_config("repos"), token=get_token("GITHUB_TOKEN")
                )
            )
        if get_config("gitlab")["enabled"]:
            prs.extend(
                FindPRsGitLab().run(
                    projects=get_config("projects"), token=get_token("GITLAB_TOKEN")
                )
            )

        if body["text"].casefold() == "mine":
            prs = filter_by(
                obj_list=prs, prop="author", values=[user.github_name, user.gitlab_name]
            )

        send_reminders(user.slack_id, prs, True)

    @staticmethod
    def _check_user_exists(user: str, users: List[User], respond):
        """
        Check the user that called the command is listed in the config.
        :param user: User ID to check for.
        :param users: Users to compare with.
        :param respond: Slack respond function.
        """
        if user not in [user.slack_id for user in users]:
            respond(
                f"Could not find your Slack ID {user} in the user map. "
                f"Please contact the service maintainer to fix this."
            )
            raise RuntimeError(
                f"User with Slack ID {user} tried using /prs but is not listed in the config."
            )

    @staticmethod
    def _check_correct_arguments(body_text: str, respond):
        """
        Check the arguments provide to the command are valid.
        :param body_text: The text provided by the command.
        :param respond: Slack respond function.
        """
        if body_text.casefold() not in ["mine", "all"]:
            respond("Please provide the correct argument: 'mine' or 'all'.")
            raise RuntimeError(
                f"User tried to run /prs with arguments {body_text}."
                f" Failed as arguments provided are not valid."
            )

    @staticmethod
    def _check_if_features_enabled(respond):
        """
        Checks that the minimum features are enabled.
        For example, both or either of the GitLab and GitHub features must be enabled.
        :param respond: Slack respond function.
        """
        if not get_config("github")["enabled"] and not get_config("gitlab")["enabled"]:
            respond("Neither of the GitHub or GitLab features are enabled.")
            raise RuntimeError(
                "Neither the GitHub or GitLab features are enabled."
                " At least one of these needs to be enabled to function."
            )
