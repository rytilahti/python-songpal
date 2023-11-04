# flake8: noqa
from importlib.metadata import version

from songpal.common import SongpalException
from songpal.device import Device
from songpal.notification import (
    ConnectChange,
    ContentChange,
    Notification,
    PowerChange,
    VolumeChange,
    ZoneActivatedChange,
)

__version__ = version("python-songpal")
