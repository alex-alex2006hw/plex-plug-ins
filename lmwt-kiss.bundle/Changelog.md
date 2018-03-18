# ChangeLog

##### 1.1.1
- _08/07/17_
  - Migrated to [USS](https://github.com/Twoure/UnSupportedServices.bundle)
  - Fixed Primewire "No Compatible Sources Found" error [PR#4](https://github.com/Twoure/lmwt-kiss.bundle/pull/4)
  - DumbTools/Prefs - Added `Xbox One` and `Apple TV v4`
  - Added new internal channel updater
  - Added `Allow Adult Content` pref _(only works with `.org` and `.is` currently)_
  - Added new License
  - Added `Genre` section

##### 1.1.0
- _05/10/16_
  - Fixed Vidzi Chromecast error, had to remove hls support
  - Added new valid site URL

##### 1.0.9
- _04/08/16_
  - Fixed Bookmark class error
  - Moved Unpacker code to shared code, can now be used with future service codes

##### 1.0.8
- _04/05/16_
  - Fixed Bookmark caching error
  - Improved URL Cache issue when _No Bookmarks_ pref selected

##### 1.0.7
- _04/04/16_
  - Added Vidzi.tv URL Service Code
  - Added HLS support for Vidzi.tv streams
  - Fixed typo in Prefs file

##### 1.0.6
- _03/11/16_
  - Fixed MediaVersion URL parse

##### 1.0.5
- _02/25/16_
- Added Refresh Bookmark Covers
  - Some thumbs/covers change over time, this will allow for fresh thumbs to be pulled
- Updated DumbPrefs, removed PHT
- New Message system, handles PHT and OpenPHT
- New Auth check for preferences and updater. Only plex server admin can edit prefs or update channel.
  - Can Auth against PMS or Plex.tv
  - Enable `Auth Admin through Plex.tv` if not Plex Home setup
  - Refer to [Comment_1133884](https://forums.plex.tv/discussion/comment/1133884/#Comment_1133884), [Comment_1133922](https://forums.plex.tv/discussion/comment/1133922/#Comment_1133922), and [Comment_1134571](https://forums.plex.tv/discussion/comment/1134571/#Comment_1134571) for breakdown of admin authentication

##### 1.0.4
- _01/23/16_
- Fixed Plex Web Search
- Updated DumbTools to latest
- Added Client Platform and Product checks in logs

##### 1.0.3
- _01/20/16_
- Added [DumbTools](https://github.com/coryo/DumbTools-for-Plex)
- Added Disable Bookmarks, so a wider range of URL domains can be tested.  FYI https sites don't usually work with this channel.

##### 1.0.2
- _12/30/15_
- Updated Channel Icon to match [piplongrun](https://github.com/piplongrun)

##### 1.0.1
- _12/23/15_
- Updates/New:
  - New: Moved bookmark code to Bookmark Class
  - New: Background Art
  - New: Changelog.md
  - Update: Moved to Release based [Updater](https://github.com/kolsys/plex-channel-updater)

##### 1.0.0
- _12/21/15_
- First Personal Release.
- **Note:** This is separate from [piplongrun](https://github.com/piplongrun)'s channel
- Fixes:
  - Improved Search. Should match Movie or TV Show regardless of movie/"tv show" search
- Updates/New:
  - New: Icons: Add/Remove Bookmarks, My Bookmarks, Update Channel, Search
  - New: Bookmarks
  - New: Readme.md
  - Update: Site URL (Domain) list.
  - Update: Optional custom Site URL
