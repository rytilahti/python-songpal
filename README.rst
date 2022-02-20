python-songpal
==============

|PyPI version| |Black|

Python 3 implementation of SongPal protocol as used by Sony's soundbar
and potentially other devices.

.. NOTE::

  This project is currently at its alpha stage and all contributions,
  whether reporting about devices working with this or creating pull
  requests to implement missing functionality are more than welcome!

Supported devices
-----------------

The library has been tested to work with following devices:

* BDV-N9200W
* CMT-SX7B
* HT-XT2, HT-XT3
* HT-NT5
* HT-MT500
* HT-ZF9
* HT-ST5000
* SRS-X77, SRS-X88, SRS-X99
* STR-DN1060, STR-DN1070, STR-DN1080


.. NOTE::

  If your device is not listed here but is working, feel free to contribute a device info file (see devinfos/ directory) by typing `songpal dump-devinfo <filename>` and creating a pull request on this repository.
  This information can later be useful for extending the support for those devices.

.. NOTE::

  Sony's `Supported devices page <http://vssupport.sony.net/en_ww/device.html>`_ lists devices,
  which will probably also work with this library.

  If you have a device which is not listed above, please create a pull request
  or an issue on github!


Getting started
---------------

Installation
~~~~~~~~~~~~

The easiest way to install is by using pip:

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

    $ songpal volume [-- output 'output title'] [<value>|mute|unmute]

    $ songpal volume 20

    $ songpal volume +5

    $ songpal volume -10

    $ songpal volume --output 'Zone 2'


    $ songpal volume --output 'Main Zone' 15

Sound Settings
--------------

Your device may support various sound-related settings,
such as night mode or adjusting the subwoofer volume.

.. code-block::

    $ songpal sound

    $ songpal sound nightMode off

    $ songpal sound subwooferLevel 4


Zone Control
--------------

.. code-block::

    $ songpal zone

    Zones:
      * Main Zone (uri: extOutput:zone?zone=1) (active)
      * Zone 2 (uri: extOutput:zone?zone=2) (active)
      * Zone 3 (uri: extOutput:zone?zone=3)
      * HDMI Zone (uri: extOutput:zone?zone=4)

    $ songpal zone 'Main Zone'

    Activating Main Zone (uri: extOutput:zone?zone=1) (active)

    $ songpal zone 'Zone 2' true

    Activating Zone 2 (uri: extOutput:zone?zone=2) (active)

    $ songpal zone 'Zone 2' false

    Deactivating Zone 2 (uri: extOutput:zone?zone=2) (active)

Input Control
--------------

without zones:
.. code-block::

    $ songpal input
          * HDMI1 (uri: extInput:hdmi?port=1)
          * HDMI2 (uri: extInput:hdmi?port=2) (active)
          * HDMI3 (uri: extInput:hdmi?port=3)

    $ songpal input HDMI1


with zones:
.. code-block::

    $ songpal input

    Inputs:
      * SOURCE (uri: extInput:source)
        - extOutput:zone?zone=2
        - extOutput:zone?zone=3
        - extOutput:zone?zone=4
      * GAME (uri: extInput:game) (active)
        - extOutput:zone?zone=1
        - extOutput:zone?zone=4
      * SAT/CATV (uri: extInput:sat-catv)
        - extOutput:zone?zone=1
        - extOutput:zone?zone=2
        - extOutput:zone?zone=3
        - extOutput:zone?zone=4
      * VIDEO 1 (uri: extInput:video?port=1)
        - extOutput:zone?zone=1
        - extOutput:zone?zone=2
        - extOutput:zone?zone=3
        - extOutput:zone?zone=4
      * VIDEO 2 (uri: extInput:video?port=2)
        - extOutput:zone?zone=1
        - extOutput:zone?zone=4
      * TV (uri: extInput:tv)
        - extOutput:zone?zone=1
      * SA-CD/CD (uri: extInput:sacd-cd)
        - extOutput:zone?zone=1
        - extOutput:zone?zone=2
        - extOutput:zone?zone=3
        - extOutput:zone?zone=4
      * Bluetooth Audio (uri: extInput:btAudio)
        - extOutput:zone?zone=1
        - extOutput:zone?zone=2
        - extOutput:zone?zone=3

    $ songpal input 'VIDEO 1'

    $ songpal input 'SOURCE' --output 'Zone 2'


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


Group Control
-------------

.. code-block::

    $ songpal group

Group command require using the UPnP URL ``--url`` instead of the API ``--endpoint``, and you'll need the ``UUIDs`` of the devices you want to group as well. Both of these can be obtained through the ``discover`` function. All group commands should be executed on the master

Creating groups:

.. code-block::

    $ songpal group --url [upnpurl] create [groupname] [slave uuids]

    $ songpal group --url "http://x.x.x.x:52323/dmr.xml" create GroupName uuid:00000000-0000-1010-8000-xxxx uuid:00000000-0000-1010-8000-xxxx

Aborting groups

.. code-block::

    $ songpal group --url [pnpurl] abort

    $ songpal group --url "http://x.x.x.x:52323/dmr.xml" abort

Changing volume

.. code-block::

    $ songpal group --url [pnpurl] volume [value -100,100]

    $ songpal group --url "http://x.x.x.x:52323/dmr.xml" volume -- -5
    $ songpal group --url "http://x.x.x.x:52323/dmr.xml" volume 5

Muting

.. code-block::

    $ songpal group --url [pnpurl] mute [true|false]

    $ songpal group --url "http://x.x.x.x:52323/dmr.xml" mute true
    $ songpal group --url "http://x.x.x.x:52323/dmr.xml" mute false



Executing custom commands
-------------------------

For experimenting it can be useful to execute arbitrary commands against the endpoint.
You can access the available methods by calling ``songpal list-all``.

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
please consider attaching the output of ``songpal dump-devinfo`` with your report.


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

.. |Black| image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black
