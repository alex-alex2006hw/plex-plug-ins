# Introduction

Imagine if all the media scattered around the internet could be found in one collection. Movies and TV Shows, of late and of yore, at your fingertips.

![dashboard-thumbnail]

Well, here it is.

**TL;DR** [Screenshot Tour][screenshots]

## Installation

Requirements:

- [Plex Media Server][media-server]
- [ss-plex.bundle][bundle-zip]
- *Optional:* curl or wget, for downloading media

After installing Plex Media Server, open the Plug-ins folder and extract ss-plex.bundle. Restart the server simply by closing and opening it again and you are ready to go.

## Usage

Once inside the channel you will find a wide scope of media. Everything is updated automatically and available to watch just about any device you can imagine: Android/iOS, PC, OS X, AppleTV, Raspberry Pi, Web Browsers support HLS or Flash, Smart TVs, DLNA (PS3/Xbox 360).

## Background

The channel is powered by a library that is based on the idea that each piece of media will have multiple sources to stream from, and to try each of those in sequence until one works. This list of sources and how to navigate the individual items is managed elsewhere. To summarize, it doesn't need to be updated.

See [ss-raspberry][ss-raspberry] for some insight into how portable this idea is.

## Frequently Asked Questions

### Q). Where will my media be downloaded?

**A).** Since the plex media server already manages your libraries for you, the channel uses the information from there. for most library configurations, this should work wonders.

If, however, you have a less typical set of libraries and you find the channel has chosen the wrong location, you may add a folder named 'ssp', 'ss-plex', 'ss potato', etc. to the proper section and that will be used instead.

Navigate to `System > Information` if you would like to know more.

### Q). There is a download reporting 100% complete, why is the queue broken?

**A).** This is an odd error that can occur. You will be presented with the option to "Repair Downloads", which will get the queue working, but there will be a video file with a '.part' extension left on your hard drive. You are free to remove that '.part' extension.

### Q). Nothing will download, what do I do?

**A).** First, make sure the channel knows where to download media, as discussed earlier.

Second, make sure you've got curl or wget installed on your system:

- **Windows**: [download a curl binary][curl-wizard] and place it in C:\Windows. wget binaries exist but installation is not as simple.
  
- **OS X**: curl works out of the box. wget can be installed through other means.
  
- **Linux**: wget is installed more often than not. curl can be installed but may not work due to issues with libcurl.so provided by Plex Media Server.

[screenshots]: http://imgur.com/a/ULaY9
[curl-wizard]: http://curl.haxx.se/dlwiz/?type=bin
[ss-raspberry]: http://github.com/mikew/ss-raspberry
[media-server]: http://plexapp.com/getplex/
[dashboard-thumbnail]: http://i.imgur.com/QfNCYCP.png
[bundle-zip]: http://mikew.github.io/ss-plex.bundle/ss-plex.bundle.zip
