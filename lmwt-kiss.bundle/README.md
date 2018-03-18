PrimeWire (formerly LetMeWatchThis)
=========

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/c0bee68f66034daeac2126f5fd8d0a68)](https://www.codacy.com/app/twoure/lmwt-kiss.bundle?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=Twoure/lmwt-kiss.bundle&amp;utm_campaign=Badge_Grade) [![GitHub issues](https://img.shields.io/github/issues/Twoure/lmwt-kiss.bundle.svg?style=flat)](https://github.com/Twoure/lmwt-kiss.bundle/issues) [![](https://img.shields.io/github/release/Twoure/lmwt-kiss.bundle.svg?style=flat)](https://github.com/Twoure/lmwt-kiss.bundle/releases)

_Keep It Simple, Stupid_ _([KISS](https://en.wikipedia.org/wiki/KISS_principle))_ _Version_

This plugin creates a new channel within [Plex Media Server](https://plex.tv/) (PMS) to view content from [PrimeWire](http://www.primewire.ag).

> **Note:** The author of this plugin has no affiliation with [PrimeWire](http://www.primewire.ag) nor the owners of the content that they host.

## Requirements

- [UnSupportedServices.bundle](https://github.com/Twoure/UnSupportedServices.bundle) must be installed

## Features

- Watch TV & Movies
- Custom Bookmarks
- Custom Site URL
- Block _Adult_ Content
- Search for TV or Movies
- Update Channel Internally

## Install

- Download latest [![](https://img.shields.io/github/release/Twoure/lmwt-kiss.bundle.svg?style=flat)](https://github.com/Twoure/lmwt-kiss.bundle/releases) and install it by following the Plex [instructions](https://support.plex.tv/hc/en-us/articles/201187656-How-do-I-manually-install-a-channel-) or the instructions below.
  - Unzip and rename the folder to **lmwt-kiss.bundle**
  - Copy **lmwt-kiss.bundle** into the PMS [Plug-ins](https://support.plex.tv/hc/en-us/articles/201106098-How-do-I-find-the-Plug-Ins-folder-) directory
  - Unix based platforms need to `chown plex:plex -R lmwt-kiss.bundle` after moving it into the [Plug-ins](https://support.plex.tv/hc/en-us/articles/201106098-How-do-I-find-the-Plug-Ins-folder-) directory _(`user:group` may differ by platform)_
  - **Restart PMS**

## Issues

- Currently there are many PrimeWire sites, but not all of them are structured the same.
- Current URL test is `Domain + '/watch-2741621-Brooklyn-Nine-Nine'`
  - Example: `http://www.primewire.ag/watch-2741621-Brooklyn-Nine-Nine`
- Allowing Adult content is still experimental and as such may not work for all sources.
  - Adult URLs only work with `primewire.org` and `primewire.is` currently (maybe `.ag` but not sure yet)
- Many sources are very low quality, not much HD content

## [Changelog](Changelog.md#changelog)

## Acknowledgements

- [piplongrun](https://github.com/piplongrun) for creating/supporting the original channel
