LihatTV.bundle
==============

This is a plugin that creates a new channel in [Plex Media Server](https://plex.tv) to view content from [LihatTV](http://lihattv.com/). It is currently under development and as such, should be considered alpha software and potentially unstable.

> **Note:** the author of this plugin has no affiliation with [LihatTV](http://lihattv.com/) nor the owners of the content that they host.

## Features

- Watch Live IPTV
- Search IPTV
- Custom Bookmarks
- Block _Adult_ Content
- Update from within the Channel

## Channel Support

##### Plex Media Server:
- Tested Working:
  - Ubuntu 14.04 LTS: PMS version 0.9.15.2
  - Windows 7 & 10: PMS version 0.9.12.13

##### Plex Clients:
- Tested Working:
  - Plex Home Theater (Ubuntu 14.04 LTS, and Windows 7 & 10)
  - Plex Media Player (Plex: 2.4.37, PMP: 1.0.3, OpenELEC(Raspberry Pi): 6.0)
  - Android (KitKat 4.4.2)
  - Plex/Web (2.5.4)
- Not Working:
  - Chromecast

## How To Install

- [Download](https://github.com/Twoure/LihatTV.bundle/releases/latest) the latest release and install LihatTV.bundle by following the Plex [instructions](https://support.plex.tv/hc/en-us/articles/201187656-How-do-I-manually-install-a-channel-) or the instructions below.
  - Unzip and rename the folder to "LihatTV.bundle"
  - Copy LihatTV.bundle into the PMS [Plug-ins](https://support.plex.tv/hc/en-us/articles/201106098-How-do-I-find-the-Plug-Ins-folder-) directory
  - ~~Restart PMS~~ **This is old, should not have to restart PMS.  If channel does not appear then Restart PMS**

## Issues

- Channel = Movies, mp4 streams are old style Google Picasa links with set timeout.  Most links have expired.
- Removed options for `mms` and `rtmp` streams.  Too many issues with compatibility in Plex Framework. May add back later.

## [Changelog](Changelog.md)
