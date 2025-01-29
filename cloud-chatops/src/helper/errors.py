"""This module contains custom exceptions to handle errors for the app."""


class ErrorInConfig(Exception):
    """Exception for problems with app configuration."""

    def __init__(self, feature, parameter):
        self.message = (
            f"There is a problem with your config.yaml."
            f" The feature {feature} does not have the parameter {parameter} set."
        )
        super().__init__(self.message)


class ErrorInSecrets(Exception):
    """Exception for problems with app secrets."""

    def __init__(self, secret):
        self.message = f"There is a problem with your secrets.yaml. The secret {secret} is not set."
        super().__init__(self.message)


class NoTestCase(LookupError):
    """Error: There is no method to test this event."""
