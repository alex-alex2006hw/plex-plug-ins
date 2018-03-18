import re
from PMS import *
from PMS.Objects import *
from PMS.Shortcuts import *

###################################################################################################

PLUGIN_TITLE               = 'MovShare'
PLUGIN_PREFIX              = '/video/movshare'

BASE_URL                   = 'http://www.movshare.net'
LOGIN                      = '%s/login.php' % BASE_URL
MOST_POPULAR               = '%s/panel.php?q=5&st=popular&s=' % BASE_URL
NEWEST                     = '%s/panel.php?q=5&st=recent&s=' % BASE_URL
OLDEST                     = '%s/panel.php?q=5&st=oldest&s=' % BASE_URL
SEARCH                     = '%s/panel.php?q=5&s=%%s' % BASE_URL
PAGE                       = '&p=%s'

# Don't change, this is just used for the "Next page" items, not to change the number of items to display on one page
VIDS_PER_PAGE              = 30

CACHE_INTERVAL             = 600

# Default artwork and icon(s)
PLUGIN_ARTWORK             = 'art-default.png'
PLUGIN_ICON_DEFAULT        = 'icon-default.png'
PLUGIN_ICON_CONFIG         = 'icon-config.png'
PLUGIN_ICON_SEARCH         = 'icon-search.png'
PLUGIN_ICON_MORE           = 'icon-more.png'

###################################################################################################

def Start():
  Plugin.AddPrefixHandler(PLUGIN_PREFIX, MainMenu, PLUGIN_TITLE, PLUGIN_ICON_DEFAULT, PLUGIN_ARTWORK)
  Plugin.AddViewGroup('DefaultListing', viewMode='List', mediaType='items')

  # Set the default MediaContainer attributes
  MediaContainer.title1    = PLUGIN_TITLE
  MediaContainer.viewGroup = 'DefaultListing'
  MediaContainer.art       = R(PLUGIN_ARTWORK)

  # Set the default cache time
  HTTP.SetCacheTime(CACHE_INTERVAL)

####################################################################################################

def CreatePrefs():
  Prefs.Add(id='username', type='text', default='', label='Username')
  Prefs.Add(id='password', type='text', default='', label='Password', option='hidden')

###################################################################################################

def MainMenu():
  dir = MediaContainer()

  dir.Append(Function(InputDirectoryItem(Search, title='Search', prompt='Search', thumb=R(PLUGIN_ICON_SEARCH))))
  dir.Append(Function(DirectoryItem(MovShare, title='Most Popular', thumb=R(PLUGIN_ICON_DEFAULT)), title='Most Popular', url=MOST_POPULAR, page=1))
  dir.Append(Function(DirectoryItem(MovShare, title='Newest', thumb=R(PLUGIN_ICON_DEFAULT)), title='Newest', url=NEWEST, page=1))
  dir.Append(Function(DirectoryItem(MovShare, title='Oldest', thumb=R(PLUGIN_ICON_DEFAULT)), title='Oldest', url=OLDEST, page=1))
  dir.Append(PrefsItem('Preferences', thumb=R(PLUGIN_ICON_CONFIG)))

  return dir

####################################################################################################

# Borrowed from the Vimeo plugin :)
def Login():
  values = {
    'user' : Prefs.Get('username'),
    'pass' : Prefs.Get('password')
  }

  x = HTTP.Request(LOGIN, values)

####################################################################################################

def MovShare(sender, title, url, page):
  dir = MediaContainer(title2=title)

  if not Prefs.Get('username') and not Prefs.Get('password'):
    return MessageContainer(header='Logging in', message='Please enter your username and password in the preferences.')

  fullUrl = url + ( PAGE % str( (page-1)*VIDS_PER_PAGE ) )

  # See if we need to log in
  content = HTTP.Request(fullUrl, errors='ignore', cacheTime=0)
  if len( re.compile('a href="panel\.php?q=5".+?Search').findall(content, re.DOTALL) ) == 0:
    Login()

  # Now check to see if we're logged in
  content = HTTP.Request(fullUrl, errors='ignore', cacheTime=0)
  if re.search('<a href="panel\.php?q=5".+?>Search', content) == False:
    return MessageContainer(header='Error logging in', message='Check your username and password in the preferences.')
  else:
    pageContent = XML.ElementFromString(content, isHTML=True)
    videos = pageContent.xpath('/html/body//div[@id="results"]//li')

    for video in videos:
      vidUrl = video.xpath('./a')[0].get('href')
      vidTitle = video.xpath('./a')[0].text.strip()
      dir.Append(Function(VideoItem(GetVideo, title=vidTitle, thumb=R(PLUGIN_ICON_DEFAULT)), url=vidUrl))

    # If this isn't the last page, add a "More ..." item
    nextCheck = pageContent.xpath('/html/body//table//a[contains(.,"Next")]')
    if len(nextCheck) > 0:
      dir.Append(Function(DirectoryItem(MovShare, title='More ...', thumb=R(PLUGIN_ICON_MORE)), title=title, url=url, page=page+1))

  return dir

####################################################################################################

def Search(sender, query):
  query = String.Quote(query, usePlus=True)
  return MovShare(sender, 'Search Results', url=(SEARCH % query), page=1)

####################################################################################################

def GetVideo(sender, url):
  content = HTTP.Request(url, errors='ignore')

  if len( re.compile('file is beeing transfered').findall(content, re.DOTALL) ) == 1:
    return None
  elif len( re.compile('click continue').findall(content, re.DOTALL) ) == 1:
    # Do an empty POST to the same page to prove we're human
    content = HTTP.Request(url, {}, errors='ignore')

  vid = re.compile('<param name="src" value="(.+?)" />').findall(content, re.DOTALL)
  if len(vid) > 0:
    return Redirect(vid[0])
  else:
    vid = re.compile('addVariable\("file","(.+?)"\)').findall(content, re.DOTALL)
    if len(vid) > 0:
      return Redirect(vid[0])
    else:
      return None
