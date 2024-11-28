"""This module contains custom exceptions to handle errors for the Application."""


class RepositoriesNotGiven(RuntimeError):
    """Error: repos supplied is empty does not contain any repositories."""


class TokensNotGiven(RuntimeError):
    """Error: Token values are either empty or not given."""


class UserMapNotGiven(RuntimeError):
    """Error: User map is empty."""


class NoTestCase(LookupError):
    """Error: There is no method to test this event."""


class SecretsInPathNotFound(ValueError):
    """Error: There is no secrets directory in the home path."""
