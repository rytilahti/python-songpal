"""Module for common types (exceptions, enums)."""

from enum import Enum, IntEnum
from typing import Optional


class DeviceErrorCode(IntEnum):
    """Error code mapping.

    https://developer.sony.com/develop/audio-control-api/api-references/error-codes
    """

    Unknown = -1
    Generic = 1
    Timeout = 2
    IllegalArgument = 3
    IllegalRequest = 5
    IllegalState = 7
    NoSuchMethod = 12
    UnsupportedVersion = 14
    UnsupportedOperation = 15


class DeviceError:
    """Container for device-given errors."""

    def __init__(self, error):
        self.error_code, self.error_message = error

    @property
    def error(self):
        """Return user-friendly error message."""
        try:
            errcode = DeviceErrorCode(self.error_code)
            return f"{errcode.name} ({errcode.value}): {self.error_message}"
        except:  # noqa: E722
            return f"Unknown error {self.error_code}: {self.error_message}"

    def __str__(self):
        return self.error


class SongpalException(Exception):
    """Custom exception class.

    This is used to wrap exceptions coming from this lib.
    In case of an error from the endpoint device, the delivered error code
    and the corresponding message is stored in `code` and `message` variables
    accordingly.
    """

    def __init__(self, message, *, error=None):
        """Overridden __init__ to allow passing an extra error message.

        This is used to pass the raw error message from the device.
        """
        super().__init__(message)
        self.message = message
        self._error = None
        if error is not None:
            self._error = DeviceError(error)

    @property
    def error(self) -> Optional[DeviceError]:
        """Return a pretty error for device-returned error."""
        return self._error

    @property
    def code(self) -> Optional[int]:
        """Return device-given error code."""
        if self.error is not None:
            return self.error.error_code
        return None

    @property
    def error_message(self) -> Optional[str]:
        """Return device-given error message."""
        if self._error is not None:
            return self._error.error_message
        return None

    def __str__(self):
        return f"{self.message}: {str(self.error)}"


class ProtocolType(Enum):
    """Protocol used for communication."""

    WebSocket = "websocket:jsonizer"
    XHRPost = "xhrpost:jsonizer"
