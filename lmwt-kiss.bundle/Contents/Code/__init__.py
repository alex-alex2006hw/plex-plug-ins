import bookmarks
import messages
from pluginupdateservice import PluginUpdateService
from DumbTools import DumbKeyboard, DumbPrefs
from AuthTools import CheckAdmin

TITLE                       = 'PrimeWire'
PREFIX                      = '/video/lmwtkiss'
GIT_REPO                    = 'Twoure/lmwt-kiss.bundle'
DEFAULT_CACHE_TIME          = CACHE_1HOUR

ICON                        = 'icon-default.png'
ART                         = 'art-default.jpg'
MOVIE_ICON                  = 'icon-movie.png'
TV_ICON                     = 'icon-tv.png'
BOOKMARK_ADD_ICON           = 'icon-add-bookmark.png'
BOOKMARK_REMOVE_ICON        = 'icon-remove-bookmark.png'
REL_URL                     = u'index.php?{}sort={}&genre={}'
SORT_LIST = (
    ('date', 'Date Added'), ('views', 'Popular'), ('ratings', 'Ratings'),
    ('favorites', 'Favorites'), ('release', 'Release Date'), ('alphabet', 'Alphabet'),
    ('featured', 'Featured')
    )

BM = bookmarks.Bookmark(PREFIX, TITLE, BOOKMARK_ADD_ICON, BOOKMARK_REMOVE_ICON)
MC = messages.NewMessageContainer(PREFIX, TITLE)
Updater = PluginUpdateService()

# Initialize first run
Updater.initial_run

####################################################################################################
def Start():

    ObjectContainer.title1 = TITLE

    DirectoryObject.thumb = R(ICON)
    DirectoryObject.art = R(ART)

    InputDirectoryObject.art = R(ART)

    VideoClipObject.art = R(ART)

    Log.Debug('*' * 80)
    Log.Debug('* Platform.OS            = {}'.format(Platform.OS))
    Log.Debug('* Platform.OSVersion     = {}'.format(Platform.OSVersion))
    Log.Debug('* Platform.CPU           = {}'.format(Platform.CPU))
    Log.Debug('* Platform.ServerVersion = {}'.format(Platform.ServerVersion))
    Log.Debug('*' * 80)

    HTTP.CacheTime = DEFAULT_CACHE_TIME
    HTTP.Headers['User-Agent'] = (
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/41.0.2272.101 Safari/537.36'
        )

    ValidatePrefs()

####################################################################################################
@handler(PREFIX, TITLE, thumb=ICON, art=ART)
def MainMenu():

    Log.Debug('*' * 80)
    Log.Debug(u'* Client.Product         = {}'.format(Client.Product))
    Log.Debug(u'* Client.Platform        = {}'.format(Client.Platform))
    Log.Debug(u'* Client.Version         = {}'.format(Client.Version))

    admin = CheckAdmin()
    oc = ObjectContainer(title2=TITLE, no_cache=Client.Product in ['Plex Web'])

    if admin:
        lvc = list()
        if Prefs['update_channel'] == 'Stable':
            # Setup Updater to track latest release
            Updater.gui_update(PREFIX + '/updater', oc, GIT_REPO, tag='latest', list_view_clients=lvc)
        else:
            # Setup Updater to track branch commits
            Updater.gui_update(PREFIX + '/updater', oc, GIT_REPO, branch='dev', list_view_clients=lvc)

    oc.add(DirectoryObject(
        key=Callback(Section, title='Movies', type='movies'), title='Movies', thumb=R(MOVIE_ICON)
        ))
    oc.add(DirectoryObject(
        key=Callback(Section, title='TV Shows', type='tv'), title='TV Shows', thumb=R(TV_ICON)
        ))

    if not Prefs['no_bm']:
        oc.add(DirectoryObject(
            key=Callback(BookmarksMain), title='My Bookmarks', thumb=R('icon-bookmarks.png')
            ))

    if Client.Product in DumbPrefs.clients:
        DumbPrefs(PREFIX, oc, title='Preferences', thumb=R('icon-prefs.png'))
    elif admin:
        oc.add(PrefsObject(title='Preferences'))

    if Client.Product in DumbKeyboard.clients:
        DumbKeyboard(PREFIX, oc, Search, dktitle='Search', dkthumb=R('icon-search.png'))
    else:
        oc.add(InputDirectoryObject(
            key=Callback(Search), title='Search', prompt='Search', thumb=R('icon-search.png')
            ))

    return oc

####################################################################################################
@route(PREFIX + '/validateprefs')
def ValidatePrefs():
    """
    Need to check urls
    if no good then block channel from running
    """

    if (Prefs['pw_site_url'] != Dict['pw_site_url']) and not Prefs['custom_url']:
        Dict['pw_site_url'] = Prefs['pw_site_url']
    elif Prefs['custom_url']:
        Dict['pw_site_url'] = Prefs['pw_site_url_custom']
    Dict.Save()
    Log.Debug('*' * 80)

    if not Prefs['no_bm']:
        try:
            test = HTTP.Request(Dict['pw_site_url'] + '/watch-2741621-Brooklyn-Nine-Nine', cacheTime=0).headers
            Log.Debug(u"* '{}' is a valid url".format(Dict['pw_site_url']))
            Log.Debug(u"* '{}' headers = {}".format(Dict['pw_site_url'], test))
            Dict['domain_test'] = 'Pass'
        except:
            Log.Debug('* \"%s\" is not a valid domain for this channel.' %Dict['pw_site_url'])
            Log.Debug('* Please pick a different URL')
            Dict['domain_test'] = 'Fail'
    else:
        try:
            test = HTTP.Request(Dict['pw_site_url'], cacheTime=0).headers
            Log.Debug(u"* '{}' headers = {}".format(Dict['pw_site_url'], test))
            Dict['domain_test'] = 'Pass'
        except:
            Log.Debug(u"* '{}' is not a valid domain for this channel.".format(Dict['pw_site_url']))
            Log.Debug('* Please pick a different URL')
            Dict['domain_test'] = 'Fail'

    Log.Debug('*' * 80)
    Dict.Save()

####################################################################################################
def DomainTest():
    """Setup MessageContainer if Dict['domain_test'] failed"""

    if Dict['domain_test'] == 'Fail':
        return MC.message_container('Error', error_message())
    return False

####################################################################################################
def error_message():
    return u'{} is NOT a Valid Site URL for this channel.  Please pick a different Site URL.'.format(Dict['pw_site_url'])

####################################################################################################
def bm_prefs_html(url, http_headers=None, cacheTime=DEFAULT_CACHE_TIME):
    if http_headers:
        http_headers.update({'User-Agent': HTTP.Headers['User-Agent']})
    else:
        http_headers = HTTP.Headers

    if not Prefs['no_bm']:
        html = HTML.ElementFromURL(url, headers=http_headers, cacheTime=cacheTime)
        return (False, html)
    else:
        try:
            html = HTML.ElementFromURL(url, headers=http_headers, cacheTime=cacheTime)
            return (False, html)
        except:
            HTTP.ClearCache()
            Log.Error(error_message())
            return (True, MC.message_container('Error', error_message()))

####################################################################################################
def setup_adult(url, html):
    """Setup pass for adult content pages, if Adult Pref set"""

    t = False
    adult_content = html.xpath('//a[starts-with(@href, "/mysettings")]')
    if Prefs['adult'] and adult_content:
        adult_href = adult_content[0].get('href')
        aurl = adult_href if adult_href.startswith('http') else Dict['pw_site_url'] + adult_href
        Log(u"* Adult pass '{}' for '{}'".format(aurl, url))
        if Regex(r'((?:tv)?.+(?:\/season\-.+\-episode\-)?)').search(url):
            t, html = bm_prefs_html(aurl, {'Referer': url}, 0)
        else:
            t, html = bm_prefs_html(aurl, {'Referer': url}, CACHE_1MINUTE)
    elif adult_content:
        Log(u'* this is an adult restricted page = {}'.format(url))
        t = True
        html = MC.message_container('Warning', 'Adult Content Blocked')
    return t, html

####################################################################################################
@route(PREFIX + '/bookmarksmain')
def BookmarksMain():
    """
    Setup Bookmark Main Menu.
    Seperate by TV or Movies
    """

    bm = Dict['Bookmarks']

    if DomainTest() != False:
        return DomainTest()
    elif not bm:
        return MC.message_container('Bookmarks', 'Bookmarks list Empty')

    oc = ObjectContainer(title2='My Bookmarks', no_cache=True)

    for key in sorted(bm.keys()):
        if len(bm[key]) == 0:
            del Dict['Bookmarks'][key]
            Dict.Save()
        else:
            if 'TV' in key:
                thumb=R(TV_ICON)
            else:
                thumb=R(MOVIE_ICON)

            oc.add(DirectoryObject(
                key=Callback(BookmarksSub, category=key),
                title=key, summary=u'Display {} Bookmarks'.format(key), thumb=thumb
                ))

    if len(oc) > 0:
        return oc
    return MC.message_container('Bookmarks', 'Bookmark list Empty')

####################################################################################################
@route(PREFIX + '/bookmarkssub')
def BookmarksSub(category):
    """List Bookmarks Alphabetically"""

    bm = Dict['Bookmarks']

    if DomainTest() != False:
        return DomainTest()
    elif not category in bm.keys():
        return MC.message_container('Error',
            u'{} Bookmarks list is dirty, or no {} Bookmark list exist.'.format(category, category))

    oc = ObjectContainer(title2=u'My Bookmarks | {}'.format(category), no_cache=True)

    for bookmark in Util.ListSortedByKey(bm[category], 'title'):
        title = bookmark['title']
        thumb = bookmark['thumb']
        url = bookmark['url']
        category = bookmark['category']
        item_id = bookmark['id']

        oc.add(DirectoryObject(
            key=Callback(MediaSubPage, title=title, category=category, thumb=thumb, item_url=url, item_id=item_id),
            title=title, thumb=thumb
            ))

    if len(oc) > 0:
        oc.add(DirectoryObject(
            key=Callback(UpdateBMCovers, category=category), title='Update Bookmark Covers',
            summary='Some Cover URL\'s change over time, Use this to update covers to current URL',
            thumb=R('icon-refresh.png')
            ))
        return oc
    return MC.message_container('Bookmarks', u'{} Bookmarks list Empty'.format(category))

####################################################################################################
@route(PREFIX + '/section')
def Section(title, type='movies', genre=None):

    if DomainTest() != False:
        return DomainTest()

    oc = ObjectContainer(title2=title)

    if not genre:
        oc.add(DirectoryObject(key=Callback(Genres, title='Genres', type=type), title='Genres'))

    section = 'tv=&' if type == 'tv' else ''
    genre = genre if genre else ''
    for s, t in SORT_LIST:
        rel_url = REL_URL.format(section, s, genre)
        oc.add(DirectoryObject(key=Callback(Media, title=t, rel_url=rel_url), title=t))

    return oc

####################################################################################################
@route(PREFIX + '/genres')
def Genres(title, type):
    if DomainTest() != False:
        return DomainTest()

    section = 'tv=&' if type == 'tv' else ''
    rel_url = u'index.php?{}'.format(section)
    html, url, error = html_from_url(rel_url, 1)
    if error:
        return MC.message_container('Error', error_message())

    oc = ObjectContainer(title2=title)
    g_list = list()
    for g in html.xpath('//a[contains(@href, "%sgenre=")]' % section.replace('=', '')):
        genre = g.get('href').split('=')[-1]
        gtitle = g.text.strip()
        if (gtitle, genre) not in g_list:
            g_list.append((gtitle, genre))

    for t, g in sorted(g_list):
        oc.add(DirectoryObject(key=Callback(Section, title=t, type=type, genre=g), title=t))

    return oc

####################################################################################################
def html_from_url(rel_url, page=int):
    t = '' if (rel_url.endswith('&') or rel_url.endswith('?')) else '&'
    url = Dict['pw_site_url'] + u'/{}{}page={}'.format(rel_url, t, page)
    error = False
    if not Prefs['no_bm']:
        if Dict['pw_site_url'] != Dict['pw_site_url_old']:
            Dict['pw_site_url_old'] = Dict['pw_site_url']
            Dict.Save()
            HTTP.ClearCache()
        html = HTML.ElementFromURL(url)
    else:
        try:
            html = HTML.ElementFromURL(url)
        except:
            HTTP.ClearCache()
            Log.Error(error_message())
            html = HTML.Element('head', 'Error')
            error = True

    return (html, url, error)

####################################################################################################
@route(PREFIX + '/media', page=int, search=bool)
def Media(title, rel_url, page=1, search=False):

    if DomainTest() != False:
        return DomainTest()

    html, url, error = html_from_url(rel_url, page)
    if error:
        return MC.message_container('Error', error_message())

    oc = ObjectContainer(title2=title, no_cache=True)

    for item in html.xpath('//div[@class="index_container"]//a[contains(@href, "/watch-")]'):
        item_url = item.get('href')
        item_title = Regex(r'^Watch +?').sub('', item.get('title'))
        item_thumb = item.xpath('./img/@src')[0]
        item_id = item_thumb.split('/')[-1].split('_')[0]

        if item_thumb.startswith('//'):
            item_thumb = u'http:{}'.format(item_thumb)
        elif item_thumb.startswith('/'):
            item_thumb = 'http://{}{}'.format(url.split('/')[2], item_thumb)

        oc.add(DirectoryObject(
            key=Callback(MediaSubPage, item_url=item_url, title=item_title, thumb=item_thumb, item_id=item_id),
            title=item_title,
            thumb=item_thumb
            ))

    next_check = html.xpath('//div[@class="pagination"]/a[last()]/@href')
    if len(next_check) > 0:
        next_check = next_check[0].split('page=')[-1].split('&')[0]
        if int(next_check) > page:
            oc.add(NextPageObject(
                key=Callback(Media, title=title, rel_url=rel_url, page=page+1),
                title='More...'
                ))

    if len(oc) > 0:
        return oc
    elif search:
        return MC.message_container('Search', u'No Search results for "{}"'.format(title))
    return MC.message_container('Error', u'No media for "{}"'.format(title))

####################################################################################################
@route(PREFIX + '/media/subpage')
def MediaSubPage(title, thumb, item_url, item_id, category=None):
    """
    Split into MediaSeason (TV) or MediaVersion (Movie)
    Include Bookmark option here
    """

    if DomainTest() != False:
        return DomainTest()

    oc = ObjectContainer(title2=title, no_cache=True)

    if not item_url.startswith('http'):
        url = Dict['pw_site_url'] + item_url
    else:
        url = item_url

    html = None
    if not category:
        t, html = bm_prefs_html(url)
        if t: return html

        t, html = setup_adult(url, html)
        if t: return html

        category = 'TV Shows' if html.xpath('//div[@class="tv_container"]') else 'Movies'

    if category == 'TV Shows':
        oc.add(DirectoryObject(
            key=Callback(MediaSeasons, url=url, title=title, thumb=thumb),
            title=title,
            thumb=thumb
            ))
    else:
        oc.add(DirectoryObject(
            key=Callback(MediaVersions, url=url, title=title, thumb=thumb),
            title=title,
            thumb=thumb
            ))

        if not html:
            t, html = bm_prefs_html(url)
            if t: return html

        trailer = html.xpath('//div[@data-id="trailer"]/iframe/@src')
        if trailer and (URLService.ServiceIdentifierForURL(trailer[0]) is not None):
            oc.add(URLService.MetadataObjectForURL(trailer[0]))

    BM.add_remove_bookmark(title, thumb, item_url, item_id, category, oc)

    return oc

####################################################################################################
@route(PREFIX + '/media/seasons')
def MediaSeasons(url, title, thumb):

    if DomainTest() != False:
        return DomainTest()

    t, html = bm_prefs_html(url)
    if t: return html

    t, html = setup_adult(url, html)
    if t: return html

    oc = ObjectContainer(title2=title)

    for season in html.xpath('//div[@class="tv_container"]//a[@data-id]/@data-id'):
        oc.add(DirectoryObject(
            key=Callback(MediaEpisodes, url=url, title=u'Season {}'.format(season), thumb=thumb),
            title=u'Season {}'.format(season),
            thumb=thumb
            ))

    return oc

####################################################################################################
@route(PREFIX + '/media/episodes')
def MediaEpisodes(url, title, thumb):

    if DomainTest() != False:
        return DomainTest()

    t, html = bm_prefs_html(url)
    if t: return html

    t, html = setup_adult(url, html)
    if t: return html

    oc = ObjectContainer(title2=title)

    for item in html.xpath('//div[@data-id="%s"]//a[contains(@href, "/tv-")]' % (title.split(' ')[-1])):
        item_title = '{} {}'.format(item.xpath('.//text()')[0].strip(), item.xpath('.//text()')[1].strip().decode('ascii', 'ignore'))
        if '0 links' in item_title.lower():
            continue

        if int(Regex(r'(\d+)').search(item.xpath('.//span[@class="tv_num_versions"]/text()')[0]).group(1)) == 0:
            continue

        item_url = item.xpath('./@href')[0]

        oc.add(DirectoryObject(
            key=Callback(MediaVersions, url=item_url, title=item_title, thumb=thumb),
            title=item_title,
            thumb=thumb
            ))

    return oc

####################################################################################################
@route(PREFIX + '/media/versions')
def MediaVersions(url, title, thumb):

    if DomainTest() != False:
        return DomainTest()
    elif not url.startswith('http'):
        url = Dict['pw_site_url'] + url

    t, html = bm_prefs_html(url)
    if t: return html

    t, html = setup_adult(url, html)
    if t: return html

    oc = ObjectContainer(title2=title, no_cache=True)
    if not is_uss_installed():
        return MC.message_container('Error', 'UnSupportedServices.bundle Required')

    summary = html.xpath('//meta[@name="description"]/@content')[0].split(' online - ', 1)[-1].split('. Download ')[0]
    for ext_url in html.xpath('//a[contains(@href, "/gohere.php?")]/@href'):
        hurl = String.Base64Decode(ext_url.split('url=')[-1].split('&')[0])
        if hurl.split('/')[2].replace('www.', '') in ['youtube.com']:
            continue

        if URLService.ServiceIdentifierForURL(hurl) is not None:
            host = Regex(r'https?\:\/\/([^\/]+)').search(hurl).group(1).replace('www.', '')
            pw_url = 'primewire:%s' %(ext_url if ext_url.startswith('//') else '/'+ext_url) + '&pw_page_url=' + url

            oc.add(DirectoryObject(
                key=Callback(MediaPlayback, url=pw_url, title=title),
                title='%s - %s' %(host, title),
                summary=summary,
                thumb=thumb
                ))

    if len(oc) != 0:
        return oc
    return MC.message_container('No Sources', 'No compatible sources found')

####################################################################################################
@route(PREFIX + '/media/playback')
def MediaPlayback(url, title):

    if DomainTest() != False:
        return DomainTest()

    Log.Debug('*' * 80)
    Log.Debug('* Client.Product         = {}'.format(Client.Product))
    Log.Debug('* Client.Platform        = {}'.format(Client.Platform))
    Log.Debug('* MediaPlayback Title    = {}'.format(title))
    Log.Debug('* MediaPlayback URL      = {}'.format(url))
    Log.Debug('*' * 80)

    oc = ObjectContainer(title2=title)
    try:
        oc.add(URLService.MetadataObjectForURL(url))
    except Exception as e:
        Log.Error(str(e))
        return MC.message_container('Warning', 'This media may have expired.')
    return oc

####################################################################################################
@route(PREFIX + '/media/search')
def Search(query=''):

    if DomainTest() != False:
        return DomainTest()

    oc = ObjectContainer(title2='Search for \"%s\"' %query)

    c_list = [('Movies', 'index.php?search_keywords={}'), ('TV Shows', 'index.php?tv=&search_keywords={}')]
    for c, url in c_list:
        rel_url = url.format(String.Quote(query, usePlus=True).lower())
        if 'TV' in c:
            thumb=R(TV_ICON)
        else:
            thumb=R(MOVIE_ICON)

        oc.add(DirectoryObject(
            key=Callback(Media, title=query, rel_url=rel_url, search=True),
            title=c, thumb=thumb
            ))

    return oc

####################################################################################################
@route(PREFIX + '/bookmarks/update/covers')
def UpdateBMCovers(category):

    bm = Dict['Bookmarks']
    bookmark_list = list()
    for bookmark in Util.ListSortedByKey(bm[category], 'title'):
        title = bookmark['title']
        thumb = bookmark['thumb']
        url = bookmark['url']
        category = bookmark['category']
        item_id = bookmark['id']

        bookmark_list.append({
            'id': item_id, 'title': title, 'url': url, 'thumb': thumb, 'category': category
            })

    Thread.Create(update_bm_thumb, bookmark_list=bookmark_list)

    return MC.message_container('Update Bookmark Covers',
        u'"{}" Bookmark covers will be updated'.format(category))

####################################################################################################
def update_bm_thumb(bookmark_list=list):

    for nbm in bookmark_list:
        category = nbm['category']
        item_id = nbm['id']
        item_url = nbm['url']

        if not item_url.startswith('http'):
            url = Dict['pw_site_url'] + item_url
        else:
            url = item_url

        html = HTML.ElementFromURL(url)
        Log.Debug('*' * 80)
        Log.Debug(u'* Updating "{}" Bookmark Cover'.format(nbm['title']))
        thumb = html.xpath('//meta[@property="og:image"]/@content')[0]
        if not thumb.startswith('http'):
            thumb = 'http:' + thumb

        Log.Debug(u'* thumb = {}'.format(thumb))
        nbm.update({'thumb': thumb})

        # delete bm first so we can re-append it with new values
        bm_c = Dict['Bookmarks'][category]
        for i in xrange(len(bm_c)):
            if bm_c[i]['id'] == item_id:
                bm_c.pop(i)
                Dict.Save()
                break

        # now append updatd bookmark to correct category
        temp = {}
        temp.setdefault(category, Dict['Bookmarks'][category]).append(nbm)
        Dict['Bookmarks'][category] = temp[category]
        Dict.Save()

        timer = int(Util.RandomInt(2, 5) + Util.Random())
        Thread.Sleep(timer)  # sleep (0-30) seconds inbetween cover updates

    return

####################################################################################################
def is_uss_installed():
    """Check install state of UnSupported Services"""

    identifiers = list()
    plugins_list = XML.ElementFromURL('http://127.0.0.1:32400/:/plugins', cacheTime=0)

    for plugin_el in plugins_list.xpath('//Plugin'):
        identifiers.append(plugin_el.get('identifier'))

    return bool('com.plexapp.system.unsupportedservices' in identifiers)
