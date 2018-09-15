from enum import Enum


class SongpalException(Exception):
    """This exception class is used to wrap exceptions coming from this lib.

    In case of an error from the endpoint device, the delivered error code
    and the corresponding message is stored in `code` and `message` variables
    accordingly.
    """

    def __init__(self, *args, error=None):
        super().__init__(*args)
        self.code = self.message = None
        if error is not None:
            self.code, self.message = error


class ProtocolType(Enum):
    """Protocol used for communication."""

    WebSocket = "websocket:jsonizer"
    XHRPost = "xhrpost:jsonizer"
