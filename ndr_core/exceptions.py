"""This module contains the set of NDR Core's exceptions."""


class NdrCoreConfigurationError(Exception):
    """Exception raised for configuration errors in my application.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message):
        """Initialize the exception with a message."""
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"NdrCoreConfigurationError: {self.message}"


class PreRenderError(Exception):
    """Exception raised for errors in the pre-rendering process."""


class NdrCorePageNotFound(Exception):
    """Exception raised when a page or a page type is not found."""
