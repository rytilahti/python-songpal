# Change Log

## [0.10](https://github.com/rytilahti/python-songpal/tree/0.10) (2019-02-17)

This release adds preliminary support for controlling devices with multiple zones (@jwiese)
and grouping of devices (@rytilahti). Two fixes for compatibility breaking changes in 
async_upnp_client and click were also fixed.

[Full Changelog](https://github.com/rytilahti/python-songpal/compare/0.0.9...0.10)

**Implemented enhancements:**

- Add multi-zone support [\#13](https://github.com/rytilahti/python-songpal/issues/13)
- \[Feature/Discussion\] Grouping / Ungrouping Devices  [\#12](https://github.com/rytilahti/python-songpal/issues/12)

**Merged pull requests:**

- Initial support for zone control [\#42](https://github.com/rytilahti/python-songpal/pull/42) ([jwiese](https://github.com/jwiese))
- Update because async\_upnp\_client changed "discover" to "search" [\#41](https://github.com/rytilahti/python-songpal/pull/41) ([jwiese](https://github.com/jwiese))
- Avoid crashing on setting changes we don't know how to handle [\#40](https://github.com/rytilahti/python-songpal/pull/40) ([rytilahti](https://github.com/rytilahti))
- Added SRS-X77 devinfo [\#39](https://github.com/rytilahti/python-songpal/pull/39) ([tobyh](https://github.com/tobyh))
- Add ability to change googlecast settings [\#38](https://github.com/rytilahti/python-songpal/pull/38) ([rytilahti](https://github.com/rytilahti))
- multi-word arguments should use dashes [\#37](https://github.com/rytilahti/python-songpal/pull/37) ([flyingclimber](https://github.com/flyingclimber))
- convert discovery to use async\_upnp\_client [\#35](https://github.com/rytilahti/python-songpal/pull/35) ([rytilahti](https://github.com/rytilahti))
- Initial support for controlling device groups [\#34](https://github.com/rytilahti/python-songpal/pull/34) ([rytilahti](https://github.com/rytilahti))


## [0.0.9](https://github.com/rytilahti/python-songpal/tree/0.0.9) (2018-12-08)

This release improves the support for notifications and fixes some minor issues.

[Full Changelog](https://github.com/rytilahti/python-songpal/compare/0.0.8...0.0.9)

**Closed issues:**

- Support for SRS-ZR5 [\#24](https://github.com/rytilahti/python-songpal/issues/24)
- Home Assistant warnings with SRS-ZR7 [\#17](https://github.com/rytilahti/python-songpal/issues/17)

**Merged pull requests:**

- Added devinfo for HT-ZF9 [\#33](https://github.com/rytilahti/python-songpal/pull/33) 
([danielpalstra](https://github.com/danielpalstra))
- Added STR-DN1060 devinfo [\#30](https://github.com/rytilahti/python-songpal/pull/30) ([jwiese](https://github.com/jwiese))
- Code formating fixes [\#28](https://github.com/rytilahti/python-songpal/pull/28) ([rytilahti](https://github.com/rytilahti))
- Adding the output for dumpdevinfo of 2 models [\#27](https://github.com/rytilahti/python-songpal/pull/27) 
([thomnico](https://github.com/thomnico))
- Add SRS-ZR7 devinfo [\#26](https://github.com/rytilahti/python-songpal/pull/26) ([pschmitt](https://github.com/pschmitt))
- Add files via upload [\#25](https://github.com/rytilahti/python-songpal/pull/25) ([little-boots](https://github.com/little-boots))

## [0.0.8](https://github.com/rytilahti/python-songpal/tree/0.0.8) (2018-08-30)

Some very minor changes, importantly avoid spammimng the logger when several volume
controllers are provided by the device.

[Full Changelog](https://github.com/rytilahti/python-songpal/compare/0.0.7...0.0.8)

**Closed issues:**

- HT-NT5 support [\#22](https://github.com/rytilahti/python-songpal/issues/22)
- Got unknowns for Input STR DN1080 [\#21](https://github.com/rytilahti/python-songpal/issues/21)
- Error when trying to run song pal after installation in venv [\#20](https://github.com/rytilahti/python-songpal/issues/20)
- Help with finding endpoint on hass.io [\#19](https://github.com/rytilahti/python-songpal/issues/19)
- command not found [\#18](https://github.com/rytilahti/python-songpal/issues/18)


## [0.0.7](https://github.com/rytilahti/python-songpal/tree/0.0.7) (2018-03-24)

First real release after getting some feedback from homeassistant users fixing various issues.

Other hilights:
* An improved support for notifications is also added, to be used later for getting changes
  immediately without polling the device.

* Support for devices implementing only the 'xhrpost' protocol using HTTP POST instead of
  websockets for communication, including some (all?) sony bravia models.
  The protocol to use is decided automatically, but can be overridden with --post or --websocket


[Full Changelog](https://github.com/rytilahti/python-songpal/compare/0.0.6...0.0.7)

**Closed issues:**

- Can't install songpal [\#16](https://github.com/rytilahti/python-songpal/issues/16)
- Got unknowns for Sysinfo [\#14](https://github.com/rytilahti/python-songpal/issues/14)
- Errors calling songpal source \[STR-DN1080\] [\#11](https://github.com/rytilahti/python-songpal/issues/11)
- Hassio error. Device - sony kdl43w756c [\#10](https://github.com/rytilahti/python-songpal/issues/10)
- htmt500 [\#9](https://github.com/rytilahti/python-songpal/issues/9)
- ST DN 1070 errors in logs [\#8](https://github.com/rytilahti/python-songpal/issues/8)
- Volume down error [\#7](https://github.com/rytilahti/python-songpal/issues/7)
- Error 'empty namespace prefix is not supported in ElementPath'  [\#6](https://github.com/rytilahti/python-songpal/issues/6)

## [0.0.6](https://github.com/rytilahti/python-songpal/tree/0.0.6) (2018-02-04)
[Full Changelog](https://github.com/rytilahti/python-songpal/compare/0.0.5...0.0.6)

## [0.0.5](https://github.com/rytilahti/python-songpal/tree/0.0.5) (2018-02-03)
[Full Changelog](https://github.com/rytilahti/python-songpal/compare/0.0.4.1...0.0.5)

## [0.0.4.1](https://github.com/rytilahti/python-songpal/tree/0.0.4.1) (2018-02-03)
[Full Changelog](https://github.com/rytilahti/python-songpal/compare/0.0.4...0.0.4.1)

## [0.0.4](https://github.com/rytilahti/python-songpal/tree/0.0.4) (2018-02-03)
[Full Changelog](https://github.com/rytilahti/python-songpal/compare/0.0.3...0.0.4)

## [0.0.3](https://github.com/rytilahti/python-songpal/tree/0.0.3) (2018-01-10)
[Full Changelog](https://github.com/rytilahti/python-songpal/compare/0.0.2...0.0.3)

**Closed issues:**

- Audio Control API [\#4](https://github.com/rytilahti/python-songpal/issues/4)
- SRS-X88 status/output [\#3](https://github.com/rytilahti/python-songpal/issues/3)
- Can't find endpoint SRS-X88 [\#2](https://github.com/rytilahti/python-songpal/issues/2)
- Error [\#1](https://github.com/rytilahti/python-songpal/issues/1)

## [0.0.2](https://github.com/rytilahti/python-songpal/tree/0.0.2) (2017-12-17)
[Full Changelog](https://github.com/rytilahti/python-songpal/compare/0.0.1...0.0.2)

## [0.0.1](https://github.com/rytilahti/python-songpal/tree/0.0.1) (2017-12-10)


\* *This Change Log was automatically generated by [github_changelog_generator](https://github.com/skywinder/Github-Changelog-Generator)*
