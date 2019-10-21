# Changelog

## [0.11.2](https://github.com/rytilahti/python-songpal/tree/0.11.2) (2019-10-21)

[Full Changelog](https://github.com/rytilahti/python-songpal/compare/0.11.1...0.11.2)

**Fixed bugs:**

- Attempt to decode JSON with unexpected mimetype [\#58](https://github.com/rytilahti/python-songpal/issues/58)

**Closed issues:**

- home assistant component can't load: No Such Method [\#46](https://github.com/rytilahti/python-songpal/issues/46)

**Merged pull requests:**

- Disable JSON content-type validation [\#59](https://github.com/rytilahti/python-songpal/pull/59) ([rytilahti](https://github.com/rytilahti))

## [0.11.1](https://github.com/rytilahti/python-songpal/tree/0.11.1) (2019-10-10)

[Full Changelog](https://github.com/rytilahti/python-songpal/compare/0.11...0.11.1)

**Closed issues:**

- TypeError: attrib\(\) got an unexpected keyword argument 'convert' [\#54](https://github.com/rytilahti/python-songpal/issues/54)
- Home Assistant lots of Songpal errors [\#52](https://github.com/rytilahti/python-songpal/issues/52)

**Merged pull requests:**

- use converter instead of convert for attrib [\#57](https://github.com/rytilahti/python-songpal/pull/57) ([rytilahti](https://github.com/rytilahti))

## [0.11](https://github.com/rytilahti/python-songpal/tree/0.11) (2019-10-10)

[Full Changelog](https://github.com/rytilahti/python-songpal/compare/0.10...0.11)

**Closed issues:**

- Got unknowns for ContentChange [\#48](https://github.com/rytilahti/python-songpal/issues/48)
- "no such option: --endpoint" error [\#47](https://github.com/rytilahti/python-songpal/issues/47)
- HT-NT5. Warnings / errors in HA log [\#36](https://github.com/rytilahti/python-songpal/issues/36)

**Merged pull requests:**

- Prepare 0.11 release [\#56](https://github.com/rytilahti/python-songpal/pull/56) ([rytilahti](https://github.com/rytilahti))
- Report unknown notification variables using debug logger [\#55](https://github.com/rytilahti/python-songpal/pull/55) ([rytilahti](https://github.com/rytilahti))
- songpal dump-devinfo \<BDV-N9200W - BDV-2014\> [\#53](https://github.com/rytilahti/python-songpal/pull/53) ([anhtuanng98](https://github.com/anhtuanng98))
- Added devinfo file for Sony CMT-SX7B [\#50](https://github.com/rytilahti/python-songpal/pull/50) ([birt](https://github.com/birt))
- Remove leftover usage of request lib [\#45](https://github.com/rytilahti/python-songpal/pull/45) ([rytilahti](https://github.com/rytilahti))

## [0.10](https://github.com/rytilahti/python-songpal/tree/0.10) (2019-02-17)

[Full Changelog](https://github.com/rytilahti/python-songpal/compare/0.0.9...0.10)

**Implemented enhancements:**

- Add multi-zone support [\#13](https://github.com/rytilahti/python-songpal/issues/13)
- \[Feature/Discussion\] Grouping / Ungrouping Devices  [\#12](https://github.com/rytilahti/python-songpal/issues/12)

**Merged pull requests:**

- Update changelog and bump version to 0.10 [\#44](https://github.com/rytilahti/python-songpal/pull/44) ([rytilahti](https://github.com/rytilahti))
- Initial support for zone control [\#42](https://github.com/rytilahti/python-songpal/pull/42) ([jwiese](https://github.com/jwiese))
- Update because async\_upnp\_client changed "discover" to "search" [\#41](https://github.com/rytilahti/python-songpal/pull/41) ([jwiese](https://github.com/jwiese))
- Avoid crashing on setting changes we don't know how to handle [\#40](https://github.com/rytilahti/python-songpal/pull/40) ([rytilahti](https://github.com/rytilahti))
- Added SRS-X77 devinfo [\#39](https://github.com/rytilahti/python-songpal/pull/39) ([tobyh](https://github.com/tobyh))
- Add ability to change googlecast settings [\#38](https://github.com/rytilahti/python-songpal/pull/38) ([rytilahti](https://github.com/rytilahti))
- multi-word arguments should use dashes [\#37](https://github.com/rytilahti/python-songpal/pull/37) ([flyingclimber](https://github.com/flyingclimber))
- convert discovery to use async\_upnp\_client [\#35](https://github.com/rytilahti/python-songpal/pull/35) ([rytilahti](https://github.com/rytilahti))
- Initial support for controlling device groups [\#34](https://github.com/rytilahti/python-songpal/pull/34) ([rytilahti](https://github.com/rytilahti))

## [0.0.9](https://github.com/rytilahti/python-songpal/tree/0.0.9) (2018-12-08)

[Full Changelog](https://github.com/rytilahti/python-songpal/compare/0.0.8...0.0.9)

**Closed issues:**

- Support for SRS-ZR5 [\#24](https://github.com/rytilahti/python-songpal/issues/24)
- Home Assistant warnings with SRS-ZR7 [\#17](https://github.com/rytilahti/python-songpal/issues/17)

**Merged pull requests:**

- Added devinfo for HT-ZF9 [\#33](https://github.com/rytilahti/python-songpal/pull/33) ([danielpalstra](https://github.com/danielpalstra))
- Added STR-DN1060 devinfo [\#30](https://github.com/rytilahti/python-songpal/pull/30) ([jwiese](https://github.com/jwiese))
- Code formating fixes [\#28](https://github.com/rytilahti/python-songpal/pull/28) ([rytilahti](https://github.com/rytilahti))
- Adding the output for dumpdevinfo of 2 models [\#27](https://github.com/rytilahti/python-songpal/pull/27) ([thomnico](https://github.com/thomnico))
- Add SRS-ZR7 devinfo [\#26](https://github.com/rytilahti/python-songpal/pull/26) ([pschmitt](https://github.com/pschmitt))
- Add files via upload [\#25](https://github.com/rytilahti/python-songpal/pull/25) ([little-boots](https://github.com/little-boots))

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
