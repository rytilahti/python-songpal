# Changelog

## [0.16](https://github.com/rytilahti/python-songpal/tree/0.16) (2023-11-06)

[Full Changelog](https://github.com/rytilahti/python-songpal/compare/release/0.15.2...0.16)

**Implemented enhancements:**

- Add defining source-address for discover [\#133](https://github.com/rytilahti/python-songpal/pull/133) (@rytilahti)
- Add support for versioned methods used by newer devices [\#132](https://github.com/rytilahti/python-songpal/pull/132) (@allistermaguire)

**Closed issues:**

- Support for TA-AN1000 [\#130](https://github.com/rytilahti/python-songpal/issues/130)
- Support for SRS-XB23?  [\#127](https://github.com/rytilahti/python-songpal/issues/127)
- Apparently missing some dependency, bunch of errors [\#126](https://github.com/rytilahti/python-songpal/issues/126)
- App doesn't work on latest python 3.11.1 [\#125](https://github.com/rytilahti/python-songpal/issues/125)
- can't find the device [\#116](https://github.com/rytilahti/python-songpal/issues/116)

**Merged pull requests:**

- Use ruff for linting and formatting [\#139](https://github.com/rytilahti/python-songpal/pull/139) (@rytilahti)
- Configure to use CI as trusted publisher [\#137](https://github.com/rytilahti/python-songpal/pull/137) (@rytilahti)
- Drop importlib\_metadata dependency [\#136](https://github.com/rytilahti/python-songpal/pull/136) (@rytilahti)
- Drop Python 3.7 support [\#135](https://github.com/rytilahti/python-songpal/pull/135) (@rytilahti)
- Add updated devinfo with version info for HT-XT3 [\#134](https://github.com/rytilahti/python-songpal/pull/134) (@rytilahti)
- Add devinfo for STR-AZ5000ES receiver [\#129](https://github.com/rytilahti/python-songpal/pull/129) (@ohmantics)

## [release/0.15.2](https://github.com/rytilahti/python-songpal/tree/release/0.15.2) (2023-03-17)

[Full Changelog](https://github.com/rytilahti/python-songpal/compare/release/0.15.1...release/0.15.2)

**Fixed bugs:**

- Songpal discover giving errors [\#122](https://github.com/rytilahti/python-songpal/issues/122)
- Python 3.11 not supported \(asyncio.coroutine has been removed\) [\#120](https://github.com/rytilahti/python-songpal/issues/120)
- Fix python 3.11 support, bump async\_upnp\_client dependency [\#121](https://github.com/rytilahti/python-songpal/pull/121) (@rytilahti)

**Closed issues:**

- SRS-ZR7 integration connection issues  [\#119](https://github.com/rytilahti/python-songpal/issues/119)

**Merged pull requests:**

- Prepare 0.15.2 [\#128](https://github.com/rytilahti/python-songpal/pull/128) (@rytilahti)

## [release/0.15.1](https://github.com/rytilahti/python-songpal/tree/release/0.15.1) (2022-09-12)

[Full Changelog](https://github.com/rytilahti/python-songpal/compare/0.15...release/0.15.1)

**Fixed bugs:**

- Fix the default value for the notification fallback callback [\#117](https://github.com/rytilahti/python-songpal/pull/117) (@Flameeyes)

**Merged pull requests:**

- Release 0.15.1 [\#118](https://github.com/rytilahti/python-songpal/pull/118) (@rytilahti)

## [0.15](https://github.com/rytilahti/python-songpal/tree/0.15) (2022-07-13)

[Full Changelog](https://github.com/rytilahti/python-songpal/compare/0.14.1...0.15)

**Breaking changes:**

- Change `get_play_info` to return info from all available zones [\#114](https://github.com/rytilahti/python-songpal/pull/114) (@jwiese)

**Merged pull requests:**

- Release 0.15 [\#115](https://github.com/rytilahti/python-songpal/pull/115) (@rytilahti)
- Depend on async\_upnp\_client \>=0.27 and fix UpnpFactory imports [\#113](https://github.com/rytilahti/python-songpal/pull/113) (@yllar)
- Notification listen refactor [\#112](https://github.com/rytilahti/python-songpal/pull/112) (@Flameeyes)

## [0.14.1](https://github.com/rytilahti/python-songpal/tree/0.14.1) (2022-03-01)

[Full Changelog](https://github.com/rytilahti/python-songpal/compare/0.14...0.14.1)

**Closed issues:**

- Inconsistency between `get_update_info` and `SoftwareUpdateChange` [\#93](https://github.com/rytilahti/python-songpal/issues/93)

**Merged pull requests:**

- Prepare 0.14.1 [\#111](https://github.com/rytilahti/python-songpal/pull/111) (@rytilahti)
- Add pyupgade to pre-commit hooks and CI [\#110](https://github.com/rytilahti/python-songpal/pull/110) (@rytilahti)
- Drop support for python 3.6 [\#109](https://github.com/rytilahti/python-songpal/pull/109) (@rytilahti)
- Use github actions instead of azure pipelines for CI [\#108](https://github.com/rytilahti/python-songpal/pull/108) (@rytilahti)
- Bugfixes for HT-A7000. [\#107](https://github.com/rytilahti/python-songpal/pull/107) (@Flameeyes)

## [0.14](https://github.com/rytilahti/python-songpal/tree/0.14) (2022-02-17)

[Full Changelog](https://github.com/rytilahti/python-songpal/compare/0.13...0.14)

**Closed issues:**

- Relaxed click requirements allow click 7, which does not work [\#103](https://github.com/rytilahti/python-songpal/issues/103)
- Unhandled 404 errors when other UPnP devices in the network [\#92](https://github.com/rytilahti/python-songpal/issues/92)
- Switch to click 8 [\#91](https://github.com/rytilahti/python-songpal/issues/91)
- Volume up works but Volume down doesn't [\#87](https://github.com/rytilahti/python-songpal/issues/87)
- Send command with Bluetooth [\#80](https://github.com/rytilahti/python-songpal/issues/80)
- SRS-ZR5: error on source + active source not indicated [\#31](https://github.com/rytilahti/python-songpal/issues/31)

**Merged pull requests:**

- Prepare 0.14 [\#106](https://github.com/rytilahti/python-songpal/pull/106) (@rytilahti)
- Require click8+ [\#105](https://github.com/rytilahti/python-songpal/pull/105) (@rytilahti)
- Relax click version requirement [\#102](https://github.com/rytilahti/python-songpal/pull/102) (@rytilahti)
- Add StorageChange notification \('notifyStorageStatus'\) [\#98](https://github.com/rytilahti/python-songpal/pull/98) (@rytilahti)
- Catch exceptions on device description file fetch [\#97](https://github.com/rytilahti/python-songpal/pull/97) (@rytilahti)
- Support for HT-A7000 [\#96](https://github.com/rytilahti/python-songpal/pull/96) (@Flameeyes)
- Fix typing mistake in get\_soundfield [\#95](https://github.com/rytilahti/python-songpal/pull/95) (@Flameeyes)
- switch to poetry-core [\#90](https://github.com/rytilahti/python-songpal/pull/90) (@dotlambda)

## [0.13](https://github.com/rytilahti/python-songpal/tree/0.13) (2020-09-01)

[Full Changelog](https://github.com/rytilahti/python-songpal/compare/0.12...0.13)

**Fixed bugs:**

- group abort command is not working [\#63](https://github.com/rytilahti/python-songpal/issues/63)

**Merged pull requests:**

- Release 0.13 [\#81](https://github.com/rytilahti/python-songpal/pull/81) (@rytilahti)
- Add Group commands to readme [\#79](https://github.com/rytilahti/python-songpal/pull/79) (@maximoei)
- Fix broken group command to use correct SessionID [\#77](https://github.com/rytilahti/python-songpal/pull/77) (@maximoei)
- Add @coro for group commands [\#76](https://github.com/rytilahti/python-songpal/pull/76) (@maximoei)
- Added STR-ZA810ES devinfo [\#75](https://github.com/rytilahti/python-songpal/pull/75) (@rfeagley)

## [0.12](https://github.com/rytilahti/python-songpal/tree/0.12) (2020-04-26)

[Full Changelog](https://github.com/rytilahti/python-songpal/compare/0.11.2...0.12)

**Fixed bugs:**

- ModuleNotFoundError: No module named 'async\_upnp\_client.search [\#51](https://github.com/rytilahti/python-songpal/issues/51)

**Closed issues:**

- use homeassistant when change source of SRS-X99 always get short disconnecting [\#69](https://github.com/rytilahti/python-songpal/issues/69)
- Hassio's latest update makes songpal disappear [\#67](https://github.com/rytilahti/python-songpal/issues/67)
- songpal command in the console [\#66](https://github.com/rytilahti/python-songpal/issues/66)
- Install in Hassio \(docker\) [\#65](https://github.com/rytilahti/python-songpal/issues/65)
- HT-RT5 support \(HT-CT790 + two SRS-ZR5\) Surround Sound [\#32](https://github.com/rytilahti/python-songpal/issues/32)

**Merged pull requests:**

- fix azure pipelines to use poetry [\#74](https://github.com/rytilahti/python-songpal/pull/74) (@rytilahti)
- Prepare 0.12 [\#73](https://github.com/rytilahti/python-songpal/pull/73) (@rytilahti)
- Handles InvalidURL and ClientConnectionError exceptions [\#72](https://github.com/rytilahti/python-songpal/pull/72) (@shenxn)
- add PlaybackFunctionChange notification [\#71](https://github.com/rytilahti/python-songpal/pull/71) (@rytilahti)
- add SRS-X99 devinfo [\#70](https://github.com/rytilahti/python-songpal/pull/70) (@FaintGhost)
- Create HT-XT2.json [\#68](https://github.com/rytilahti/python-songpal/pull/68) (@kurt-k)
- Added notifications for zone activation status [\#64](https://github.com/rytilahti/python-songpal/pull/64) (@jwiese)
- use azure pipelines instead of travis [\#61](https://github.com/rytilahti/python-songpal/pull/61) (@rytilahti)

## [0.11.2](https://github.com/rytilahti/python-songpal/tree/0.11.2) (2019-10-21)

[Full Changelog](https://github.com/rytilahti/python-songpal/compare/0.11.1...0.11.2)

**Fixed bugs:**

- Attempt to decode JSON with unexpected mimetype [\#58](https://github.com/rytilahti/python-songpal/issues/58)

**Closed issues:**

- home assistant component can't load: No Such Method [\#46](https://github.com/rytilahti/python-songpal/issues/46)

**Merged pull requests:**

- Disable JSON content-type validation [\#59](https://github.com/rytilahti/python-songpal/pull/59) (@rytilahti)

## [0.11.1](https://github.com/rytilahti/python-songpal/tree/0.11.1) (2019-10-10)

[Full Changelog](https://github.com/rytilahti/python-songpal/compare/0.11...0.11.1)

**Closed issues:**

- TypeError: attrib\(\) got an unexpected keyword argument 'convert' [\#54](https://github.com/rytilahti/python-songpal/issues/54)
- Home Assistant lots of Songpal errors [\#52](https://github.com/rytilahti/python-songpal/issues/52)

**Merged pull requests:**

- use converter instead of convert for attrib [\#57](https://github.com/rytilahti/python-songpal/pull/57) (@rytilahti)

## [0.11](https://github.com/rytilahti/python-songpal/tree/0.11) (2019-10-10)

[Full Changelog](https://github.com/rytilahti/python-songpal/compare/0.10...0.11)

**Closed issues:**

- Got unknowns for ContentChange [\#48](https://github.com/rytilahti/python-songpal/issues/48)
- "no such option: --endpoint" error [\#47](https://github.com/rytilahti/python-songpal/issues/47)
- HT-NT5. Warnings / errors in HA log [\#36](https://github.com/rytilahti/python-songpal/issues/36)

**Merged pull requests:**

- Prepare 0.11 release [\#56](https://github.com/rytilahti/python-songpal/pull/56) (@rytilahti)
- Report unknown notification variables using debug logger [\#55](https://github.com/rytilahti/python-songpal/pull/55) (@rytilahti)
- songpal dump-devinfo \<BDV-N9200W - BDV-2014\> [\#53](https://github.com/rytilahti/python-songpal/pull/53) (@anhtuanng98)
- Added devinfo file for Sony CMT-SX7B [\#50](https://github.com/rytilahti/python-songpal/pull/50) (@birt)
- Remove leftover usage of request lib [\#45](https://github.com/rytilahti/python-songpal/pull/45) (@rytilahti)

## [0.10](https://github.com/rytilahti/python-songpal/tree/0.10) (2019-02-17)

[Full Changelog](https://github.com/rytilahti/python-songpal/compare/0.0.9...0.10)

**Implemented enhancements:**

- Add multi-zone support [\#13](https://github.com/rytilahti/python-songpal/issues/13)
- \[Feature/Discussion\] Grouping / Ungrouping Devices  [\#12](https://github.com/rytilahti/python-songpal/issues/12)

**Merged pull requests:**

- Update changelog and bump version to 0.10 [\#44](https://github.com/rytilahti/python-songpal/pull/44) (@rytilahti)
- Initial support for zone control [\#42](https://github.com/rytilahti/python-songpal/pull/42) (@jwiese)
- Update because async\_upnp\_client changed "discover" to "search" [\#41](https://github.com/rytilahti/python-songpal/pull/41) (@jwiese)
- Avoid crashing on setting changes we don't know how to handle [\#40](https://github.com/rytilahti/python-songpal/pull/40) (@rytilahti)
- Added SRS-X77 devinfo [\#39](https://github.com/rytilahti/python-songpal/pull/39) (@tobyh)
- Add ability to change googlecast settings [\#38](https://github.com/rytilahti/python-songpal/pull/38) (@rytilahti)
- multi-word arguments should use dashes [\#37](https://github.com/rytilahti/python-songpal/pull/37) (@flyingclimber)
- convert discovery to use async\_upnp\_client [\#35](https://github.com/rytilahti/python-songpal/pull/35) (@rytilahti)
- Initial support for controlling device groups [\#34](https://github.com/rytilahti/python-songpal/pull/34) (@rytilahti)

## [0.0.9](https://github.com/rytilahti/python-songpal/tree/0.0.9) (2018-12-08)

[Full Changelog](https://github.com/rytilahti/python-songpal/compare/0.0.8...0.0.9)

**Closed issues:**

- Support for SRS-ZR5 [\#24](https://github.com/rytilahti/python-songpal/issues/24)
- Home Assistant warnings with SRS-ZR7 [\#17](https://github.com/rytilahti/python-songpal/issues/17)

**Merged pull requests:**

- Added devinfo for HT-ZF9 [\#33](https://github.com/rytilahti/python-songpal/pull/33) (@danielpalstra)
- Added STR-DN1060 devinfo [\#30](https://github.com/rytilahti/python-songpal/pull/30) (@jwiese)
- Code formating fixes [\#28](https://github.com/rytilahti/python-songpal/pull/28) (@rytilahti)
- Adding the output for dumpdevinfo of 2 models [\#27](https://github.com/rytilahti/python-songpal/pull/27) (@thomnico)
- Add SRS-ZR7 devinfo [\#26](https://github.com/rytilahti/python-songpal/pull/26) (@pschmitt)
- Add files via upload [\#25](https://github.com/rytilahti/python-songpal/pull/25) (@little-boots)

## [0.0.8](https://github.com/rytilahti/python-songpal/tree/0.0.8) (2018-08-30)

[Full Changelog](https://github.com/rytilahti/python-songpal/compare/0.0.7...0.0.8)

**Closed issues:**

- HT-NT5 support [\#22](https://github.com/rytilahti/python-songpal/issues/22)
- Got unknowns for Input STR DN1080 [\#21](https://github.com/rytilahti/python-songpal/issues/21)
- Error when trying to run song pal after installation in venv [\#20](https://github.com/rytilahti/python-songpal/issues/20)
- Help with finding endpoint on hass.io [\#19](https://github.com/rytilahti/python-songpal/issues/19)
- command not found [\#18](https://github.com/rytilahti/python-songpal/issues/18)

## [0.0.7](https://github.com/rytilahti/python-songpal/tree/0.0.7) (2018-03-24)

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

[Full Changelog](https://github.com/rytilahti/python-songpal/compare/135450b001321e413163a4b3803b8746804aea59...0.0.1)



\* *This Changelog was automatically generated by [github_changelog_generator](https://github.com/github-changelog-generator/github-changelog-generator)*
