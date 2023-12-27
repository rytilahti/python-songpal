# flake8: noqa
from importlib.metadata import version

from songpal.common import SongpalException
from songpal.device import Device
from songpal.notification import (
    ConnectChange,
    ContentChange,
    Notification,
    NotificationChange,
    PowerChange,
    SettingChange,
    SoftwareUpdateChange,
    VolumeChange,
    ZoneActivatedChange,
)

__version__ = version("python-songpal")
