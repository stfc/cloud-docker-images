"""This module contains custom exceptions to handle errors for the Application."""


class RepoNotFound(LookupError):
    """Error: The requested repository does not exist on GitHub."""


class UnknownHTTPError(RuntimeError):
    """Error: The received HTTP response is unexpected."""


class RepositoriesNotGiven(RuntimeError):
    """Error: repos.csv does not contain any repositories."""


class TokensNotGiven(RuntimeError):
    """Error: Token values are either empty or not given."""


class UserMapNotGiven(RuntimeError):
    """Error: User map is empty."""


class BadGitHubToken(RuntimeError):
    """Error: GitHub REST Api token is invalid."""


class ChannelNotFound(LookupError):
    """Error: The channel was not found."""
