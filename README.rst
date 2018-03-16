python-songpal
==============

|PyPI version|

Python 3 implementation of SongPal protocol as used by Sony's soundbar
and potentially other devices.

.. NOTE::

  This project is currently at its alpha stage and all contributions,
  whether reporting about devices working with this or creating pull
  requests to implement missing functionality are more than welcome!

Supported devices
-----------------

The library has been tested for now with following devices:

* HT-XT3
* HT-MT500
* SRS-X88
* STR-DN1060, STR-DN1070, STR-DN1080 (no multizone support yet)


.. NOTE::
  Sony's `Supported devices page <http://vssupport.sony.net/en_ww/device.html>`_ lists devices,
  which will probably also work with this library.

  If you have a device which is not listed above, please create a pull request
  or an issue on github!


Getting started
---------------

Installation
~~~~~~~~~~~~

The easiest way for installing this project is by using pypi inside a virtualenv.

.. code-block::

    $ pip install python-songpal

Locating the endpoint
~~~~~~~~~~~~~~~~~~~~~
To communicate with the device you need to locate its endpoint URL.
The easiest way to do is to execute the discover command:

.. code-block::

    $ songpal discover

    Discovering for 3 seconds
    Found HT-XT3 - BAR-2015
    * API version: 1.0
    * Endpoint: http://192.168.1.1:10000/sony
    * Services:
      - Service: guide
      - Service: system
      - Service: audio
      - Service: avContent


This will run a UPnP discovery to find out responsive devices
implementing the ScalarWebAPI.

.. WARNING::
  If you are running the command on another network than the device
  is residing, you will need to locate the endpoint with some other means.

The endpoint can be defined with ``--endpoint`` option, or alternatively
``SONGPAL_ENDPOINT`` environment variable can be set.

General Usage
~~~~~~~~~~~~~

The accompanied ``songpal`` tool can be used to control your device.
All available commands can be listed with ``--help`` and more help on each
command can be obtained by passing it to the sub-command, e.g., ``songpal power --help``.
Most interesting commands are most likely ``power``, ``output``, ``volume``, and ``sound``.

Generally speaking invoking a command without any parameters will display
some relevant information like settings or active output.

For debugging ``-d`` (``--debug``) can be passed
-- also multiple times for increased verbosity -- for
protocol-level information.

Some of the commands can be used to adjust settings related to that functionality,
usually by passing the `target` and its wanted `value` as parameters to the command.

.. code-block::

    $ songpal bluetooth mode off

On commands which are not mainly used for settings, such as power_, require
explicit `set` sub-command for changing the settings.

.. WARNING::

   Refer to help of the specific command to find the correct format.

   TODO: Make the CLI consistent on this.

Status
------

.. code-block::

    $ songpal status


will display some basic information about the device,
such as whether it is powered on and what are its volume settings.

.. _power:

Power Control
-------------

``power`` command can be used to both turning the device on and off,
and change its power settings.

.. code-block:: bash

    $ songpal power

    $ songpal power settings

    $ songpal power

    $ songpal power set quickStartMode on

.. NOTE::
   For turning on the device the quick boot has to be activated;
   a patch for adding wake-on-lan support to allow starting the device
   without quick boot are welcome.

.. WARNING::
   The device seems to report sometimes its status to be off even
   when that is not the case (may be related to quick boot mode being 'on').

   Please enable it and restart the device fully before reporting a bug
   related to this.

Volume Control
--------------

.. code-block::

    $ songpal volume [<value>|mute|unmute]

    $ songpal volume 20

    $ songpal volume +5

    $ songpal volume -10

Sound Settings
--------------

Your device may support various sound-related settings,
such as night mode or adjusting the subwoofer volume.

.. code-block::

    $ songpal sound

    $ songpal sound nightMode off

    $ songpal sound subwooferLevel 4

Output Control
--------------

.. code-block::

    $ songpal output

    Outputs:
      * TV (uri: extInput:tv)
      * HDMI1 (uri: extInput:hdmi?port=1)
      * HDMI2 (uri: extInput:hdmi?port=2) (active)
      * HDMI3 (uri: extInput:hdmi?port=3)
      * Bluetooth Audio (uri: extInput:btAudio)
      * Analog (uri: extInput:line)

    $ songpal output HDMI1


Device Settings
---------------

To list available settings, use ``settings`` command.

.. code-block:: bash

    $ songpal settings


Do note that some settings (e.g. bluetooth settings) are not listed in the
global settings tree, but have to be separatedly accessed using the ``bluetooth`` command.

.. NOTE::

    Setting global settings directly via the CLI is not currently supported,
    but can potentially be accessed via their respective commands:
    ``bluetooth``, ``sound``, ``power``.

    Patches improving this are welcome!


Executing custom commands
-------------------------

For experimenting it can be useful to execute arbitrary commands against the endpoint.
You can access the available methods by calling ``songpal list_all``.

``command`` can be used for that as follows:

.. code-block::

    $ songpal command system getSystemInformation


Notification support
--------------------

The protocol supports subscribing to notifications on subsystem basis.
Executing `songpal notifications` without any parameters will list
available notifications.

Every notification can be listened to separately, or alternatively
all notifications from a single subsystem can be subscribed to.

.. code-block::

    $ songpal notifications --listen-all avContent

Contributing
------------

Reporting bugs or supported devices
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When reporting bugs or informing about supported device not listed above,
please consider attaching the output of ``songpal dump_devinfo`` with your report.


API information
~~~~~~~~~~~~~~~

`Audio Control API <https://developer.sony.com/develop/audio-control-api/>`_ describes
the API this project (currently partially) implements.

The `Camera Remote API <https://developer.sony.com/develop/cameras/get-started/>`_
is also similar to this, and may also be useful for developers.


Home Assistant support
----------------------

Home Assistant supports devices using this library directly since 0.65: https://home-assistant.io/components/media_player.songpal/


.. |PyPI version| image:: https://badge.fury.io/py/python-songpal.svg
   :target: https://badge.fury.io/py/python-songpal
