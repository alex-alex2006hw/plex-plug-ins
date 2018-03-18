####################################################################################################
#                                                                                                  #
#                                     LihatTV Plex Channel                                         #
#                                                                                                  #
####################################################################################################
from updater import Updater
from DumbTools import DumbKeyboard
from DumbTools import DumbPrefs

# set global variables
TITLE = L('title')
PREFIX = '/video/lihattv'

# set background art and icon defaults
ICON = 'icon-default.png'
ART = 'art-default.jpg'
VIDEO_ICON = 'icon-video.png'
VIDEO_THUMB = 'thumb-video.png'
DEFAULT_ICON = 'icon-art.png'
COUNTRY_ICON = 'icon-countries.png'
GENRE_ICON = 'icon-genres.png'
ALL_ICON = 'icon-listview.png'
NEXT_ICON = 'icon-next.png'
BOOKMARK_ICON = 'icon-bookmark.png'
BOOKMARK_ADD_ICON = 'icon-add-bookmark.png'
BOOKMARK_REMOVE_ICON = 'icon-remove-bookmark.png'
SEARCH_ICON = 'icon-search.png'
PREFS_ICON = 'icon-prefs.png'

####################################################################################################
def Start():
    HTTP.CacheTime = 0

    ObjectContainer.title1 = TITLE
    ObjectContainer.art = R(ART)

    DirectoryObject.thumb = R(DEFAULT_ICON)
    DirectoryObject.art = R(ART)

    InputDirectoryObject.art = R(ART)

    VideoClipObject.art = R(ART)

    ValidatePrefs(start=True)

####################################################################################################
@handler(PREFIX, TITLE, ICON, ART)
def MainMenu():
    oc = ObjectContainer(title2=TITLE, no_cache=True)

    Updater(PREFIX + '/updater', oc)
    oc.add(DirectoryObject(key=Callback(DirectoryList, page=1), title='All', thumb=R(ALL_ICON)))
    oc.add(DirectoryObject(key=Callback(CountryList), title='Countries', thumb=R(COUNTRY_ICON)))
    oc.add(DirectoryObject(key=Callback(GenreList), title='Genres', thumb=R(GENRE_ICON)))
    oc.add(DirectoryObject(key=Callback(BookmarksMain), title='My Bookmarks', thumb=R(BOOKMARK_ICON)))
    if Client.Product in DumbPrefs.clients:
        DumbPrefs(PREFIX, oc, title='Preferences', thumb=R(PREFS_ICON))
    else:
        oc.add(PrefsObject(title='Preferences', thumb=R(PREFS_ICON)))
    if Client.Product in DumbKeyboard.clients:
        DumbKeyboard(PREFIX, oc, Search, dktitle='Search', dkthumb=R(SEARCH_ICON))
    else:
        oc.add(InputDirectoryObject(
            key=Callback(Search),
            title='Search', summary='Search LihatTV', prompt='Search for...',
            thumb=R(SEARCH_ICON)
            ))

    return oc

####################################################################################################
@route(PREFIX + '/validateprefs', start=bool)
def ValidatePrefs(start=False):
    """Validate domain"""

    # Test domain url
    if not Dict['domain']:
        Dict['domain'] = Prefs['domain']

    if (Prefs['domain'] != Dict['domain']) or (start == True):
        Dict['domain'] = Prefs['domain']
        url = 'http://' + Prefs['domain'] + '/admin/list.php'
        try:
            test = HTTP.Request(url).content
            if test == 'Can\'t connecting...':
                Logger('*' * 80, force=True)
                Logger('* test failed', kind='Warn', force=True)
                Logger('*' * 80, force=True)
                Dict['domain_test'] = 'Fail'
            else:
                Dict['domain_test'] = 'Pass'
                Logger('*' * 80, force=True)
                Logger('* %s Domain Passed Test' %Prefs['domain'], force=True)
                Logger('*' * 80, force=True)
        except:
            Logger('*' * 80, force=True)
            Logger('* Test failed. %s domain offline.' %Prefs['domain'], kind='Warn', force=True)
            Logger('*' * 80, force=True)
            Dict['domain_test'] = 'Fail'

    Dict.Save()

####################################################################################################
def DomainTest():
    """Setup MessageContainer if Dict[\'domain_test\'] failed"""

    if Dict['domain_test'] == 'Fail':
        return (False, MessageContainer(
            'Error',
            'Domain %s offline. Please pick a different Domain.' %Prefs['domain']))
    else:
        return (True, None)

####################################################################################################
@route(PREFIX + '/bookmarksmain')
def BookmarksMain():
    """Setup Bookmark Main Menu. Create Genre Sub-directories"""

    if not Dict['Bookmarks']:
        return MessageContainer('Bookmarks', 'No Bookmarks yet. Get out there and start adding some!!!')

    oc = ObjectContainer(title2='My Bookmarks')

    for key in sorted(Dict['Bookmarks'].keys()):
        if not Prefs['adult'] and 'adult' in key.lower():
            continue
        elif len(Dict['Bookmarks'][key]) == 0:
            del Dict['Bookmarks'][key]
            Dict.Save()
        else:
            oc.add(DirectoryObject(
                key=Callback(BookmarksSub, genre=key),
                title=key, summary='Display %s Bookmarks' %key
                ))

    if len(oc) > 0:
        return oc
    else:
        return MessageContainer('Warning', 'No Bookmarks yet. Get out there and start adding some!!!')

####################################################################################################
@route(PREFIX + '/bookmarkssub')
def BookmarksSub(genre):
    """Display Bookmarks"""

    if not genre in Dict['Bookmarks'].keys():
        return MessageContainer(
            'Error',
            '%s Bookmarks list is dirty, or no %s Bookmark list exist.' %(genre, genre))

    oc = ObjectContainer(title2='My Bookmarks | %s' %genre)

    for bookmark in sorted(Dict['Bookmarks'][genre], key=lambda k: k['title']):
        video_info = {
            'title': bookmark['title'],
            'summary': bookmark['summary'],
            'tagline': bookmark['summary'],
            'genres': bookmark['genre'],
            'countries': bookmark['country'],
            'thumb': bookmark['thumb'],
            'art': bookmark['art'],
            'id': bookmark['id'],
            'url': 'http://' + Prefs['domain'] + '/?play=' + bookmark['id']
            }

        if not Prefs['adult'] and 'adult' in (bookmark['genre'][0].lower() if bookmark['genre'] else ''):
            continue
        else:
            oc.add(DirectoryObject(
                key=Callback(VideoOptionPage, video_info=video_info),
                title='%s | ID: %s' %(video_info['title'], video_info['id']),
                summary=video_info['summary'], tagline=video_info['tagline'],
                thumb=R(video_info['thumb']) if video_info['thumb'] else None,
                art=R(video_info['art']) if video_info['art'] else None
                ))

    if len(oc) > 0:
        return oc
    else:
        return MessageContainer('Bookmarks', 'No Bookmarks yet. Get out there and start adding some!!!')

####################################################################################################
@route(PREFIX + '/genrelist')
def GenreList():
    """Get Genres for relevant category and stream"""

    test, message = DomainTest()
    if not test:
        return message

    main_title = 'Genres'
    oc = ObjectContainer(title2=main_title)

    stream = '.m3u8'
    channel = 'tv'
    q = '/api/?q=genre&channel=%s&stream=%s' %(channel, stream)
    url = 'http://' + Prefs['domain'] + q

    html = HTML.ElementFromURL(url)

    genres = html.xpath('//option/text()')
    for genre in sorted(genres):
        if not Prefs['adult'] and 'adult' in genre.lower():
            continue
        else:
            oc.add(DirectoryObject(
                key=Callback(DirectoryList, genre=genre, page=1),
                title=genre, summary='%s TV List ' %genre
                ))

    return oc

####################################################################################################
@route(PREFIX + '/coutnrylist')
def CountryList():
    """Setup Country List, some countries will not have streams"""

    test, message = DomainTest()
    if not test:
        return message

    main_title = 'Countries'
    oc = ObjectContainer(title2=main_title)

    stream = '.m3u8'
    channel = 'tv'
    q = '/api/?q=country&channel=%s&stream=%s' %(channel, stream)
    url = 'http://' + Prefs['domain'] + q

    html = HTML.ElementFromURL(url)
    countries = html.xpath('//option/text()')
    for country in sorted(countries):
        oc.add(DirectoryObject(
            key=Callback(DirectoryList, country=country, page=1),
            title=country, summary='%s Country List ' %country
            ))

    return oc

####################################################################################################
@route(PREFIX + '/search')
def Search(query=''):
    """Currently search is just for \"TV Channel\""""

    (test, message) = DomainTest()
    if not test:
        return message

    search = String.Quote(query, usePlus=True)

    q = '/api/?q=xml&channel=TV&stream=.m3u8&search=%s&limit=1&page=1' %query
    url = 'http://' + Prefs['domain'] + q
    page_info = HTTP.Request(url).content.splitlines()
    page_el = XML.ElementFromString(page_info[0] + page_info[-1])
    if not int(page_el.get('total')) == 0:
        return DirectoryList(page=1, query=query)
    else:
        return MessageContainer('Search Warning',
            'There are no search results for \"%s\". Try being less specific.' %query)

####################################################################################################
@route(PREFIX + '/directorylist', page=int)
def DirectoryList(page, genre='', country='', query=''):
    """
    Return Channels based on input
    Genre, Country and Search are sent here
    """

    (test, message) = DomainTest()
    if not test:
        return message

    stream = '.m3u8'
    limit = 500

    if not genre:
        genre = ''

    if not country:
        country = ''

    if not query:
        query = ''

    q = (
        '/api/?q=xml&channel=TV&genre=%s&country=%s&stream=%s&search=%s&limit=%i&page=%i'
        %(genre, country, stream, query, limit, page)
        )
    Logger('*' * 80)
    Logger('* q = %s' %q)
    url = 'http://' + Prefs['domain'] + q

    page_info = HTTP.Request(url).content.splitlines()
    r_info = page_info[0] + page_info[-1]
    Logger('* r_info = %s' %r_info)
    page_el = XML.ElementFromString(r_info)
    total = int(page_el.get('total'))
    if total == 0 and not genre == '':
        return MessageContainer('Warning', 'No %s Streams for %s TV List' %(stream, genre))
    elif total == 0 and not country == '':
        return MessageContainer('Warning', 'No %s Streams for %s TV List' %(stream, country))

    total_pgs = int(total/limit) + 1
    Logger('* total pages = %i' %total_pgs)
    Logger('* current page = %i' %page)

    if page == 1 and total_pgs == 1:
        if query:
            main_title = 'Search: \"%s\"' %query
        elif genre or country:
            main_title = 'Genre | %s' %genre if genre else 'Country | %s' %country
        else:
            main_title = 'TV'
    elif 1 < total_pgs == page:
        if query:
            main_title = 'Search: \"%s\" | Last page' %query
        elif genre or country:
            main_title = ('Genre | %s' %genre if genre else 'Country | %s' %country) + ' | Last Page'
        else:
            main_title = 'Last Page'
    elif 1 < total_pgs > page:
        if query:
            main_title = 'Search: \"%s\" | Page %i of %i' %(query, page, total_pgs)
        elif genre or country:
            main_title = ('Genre | %s' %genre if genre else 'Country | %s' %country) + ' | Page %i of %i' %(page, total_pgs)
        else:
            main_title = 'Page %i of %i' %(page, total_pgs)

    oc = ObjectContainer(title2=main_title)

    # setup url to parse html page
    q2 = (
        '/api/?q=html&channel=TV&genre=%s&country=%s&stream=%s&search=%s&limit=%i&page=%i'
        %(genre, country, stream, query, limit, page)
        )
    url2 = 'http://' + Prefs['domain'] + q2

    xml = HTML.ElementFromURL(url2, encoding='utf8', errors='ignore')

    for node in xml.xpath('//ol/li'):
        title_text = node.text_content().strip()
        r = Regex('^(.+).+\((.+)[:](.+?)\ .(.+?)\)').search(title_text)
        ch_title = r.group(1).strip()
        ch_category = r.group(2).strip()
        ch_genre = r.group(3).strip()
        ch_country = r.group(4).strip()
        ch_url = node.xpath('./a/@href')[0].strip()
        video_id = str(ch_url.split('=')[1])
        tagline = 'Category: %s | ID: %s | Genre: %s | Country: %s' %(ch_category, video_id, ch_genre, ch_country)

        video_info = {
            'title': ch_title,
            'summary': tagline,
            'tagline': tagline,
            'genres': [ch_genre],
            'countries': [ch_country],
            'thumb': VIDEO_THUMB,
            'art': ART,
            'id': video_id,
            'url': ch_url
            }

        if not Prefs['adult'] and 'adult' in ch_genre.lower():
            continue
        else:
            oc.add(DirectoryObject(
                key=Callback(VideoOptionPage, video_info=video_info),
                title='%s | ID: %s' %(ch_title, video_id), summary=tagline,
                tagline=tagline, thumb=R(VIDEO_ICON)
                ))

    if page < total_pgs and len(oc) > 0:
        oc.add(NextPageObject(
            key=Callback(DirectoryList,
                page=int(page) + 1, genre=genre, country=country, query=query),
            title='Next Page>>', thumb=R(NEXT_ICON)
            ))

    Logger('*' * 80)

    if len(oc) > 0:
        return oc
    else:
        return MessageContainer('Warning', 'No Streams Found')

####################################################################################################
@route(PREFIX + '/videooptionpage', video_info=dict)
def VideoOptionPage(video_info):
    """VideoObject and Bookmark function"""

    test, message = DomainTest()
    if not test:
        return message

    genre = video_info['genres'][0] if video_info['genres'] else 'Unknown'
    bm = Dict['Bookmarks']
    match =  ((True if [b['id'] for b in bm[genre] if b['id'] == video_info['id']] else False) if genre in bm.keys() else False) if bm else False
    description = None
    Logger('*' * 80)

    if match:
        v_url = video_info['url']
        if 'player' in v_url:
            url_node = v_url.split('?')
            url_base = url_node[0]
            url_id = url_node[1].split('=')[1]
            v_url = url_base + '?play=' + url_id

        html = HTML.ElementFromURL(v_url)
        description = html.xpath('//head/meta[@name="description"]')[0].get('content')
        if description == '404: THIS CHANNEL NOT FOUND':
            Logger('* 404 Channel. \"%s | %s\" Channel not found' %(video_info['id'], video_info['title']))
            oc = ObjectContainer(
                title2=video_info['title'], header='Warning',
                message='\"%s | %s\" Channel Offline. Try again later.' %(video_info['id'], video_info['title'])
                )
    Logger('* match = %s' %match)

    if description != '404: THIS CHANNEL NOT FOUND':
        Logger('* \"%s | %s\" Channel Online.' %(video_info['id'], video_info['title']))
        oc = ObjectContainer(title2=video_info['title'])

        oc.add(VideoClipObject(
            title=video_info['title'],
            summary=video_info['summary'],
            tagline=video_info['tagline'],
            genres=video_info['genres'],
            countries=video_info['countries'],
            thumb=R(video_info['thumb']),
            art=R(video_info['art']),
            url=video_info['url']
            ))

    if match:
        Logger('* Remove \"%s | %s\" from bookmarks' %(video_info['id'], video_info['title']))
        oc.add(DirectoryObject(
            key=Callback(RemoveBookmark, video_info=video_info),
            title='Remove Bookmark',
            summary='Remove \"%s | %s\" from your Bookmarks list.' %(video_info['id'], video_info['title']),
            thumb=R(BOOKMARK_REMOVE_ICON)
            ))
    else:
        Logger('* Add \"%s | %s\" to bookmarks' %(video_info['id'], video_info['title']))
        oc.add(DirectoryObject(
            key=Callback(AddBookmark, video_info=video_info),
            title='Add Bookmark',
            summary='Add \"%s | %s\" to your Bookmarks list.' %(video_info['id'], video_info['title']),
            thumb=R(BOOKMARK_ADD_ICON)
            ))
    Logger('*' * 80)

    return oc

####################################################################################################
@route(PREFIX + '/addbookmark', video_info=dict)
def AddBookmark(video_info):
    """Add Bookmark"""

    genre = video_info['genres'][0] if video_info['genres'] else 'Unknown'

    new_bookmark = {
        'title': video_info['title'], 'id': video_info['id'], 'genre': video_info['genres'],
        'country': video_info['countries'], 'summary': video_info['summary'],
        'thumb': video_info['thumb'], 'art': video_info['art']
        }
    bm = Dict['Bookmarks']

    if not bm:
        Dict['Bookmarks'] = {genre: [new_bookmark]}
        Dict.Save()

        return MessageContainer('Bookmarks',
            '\"%s | %s\" has been added to your bookmarks.' %(video_info['id'], video_info['title']))
    elif genre in bm.keys():
        Logger('*' * 80)
        if (True if [b['id'] for b in bm[genre] if b['id'] == video_info['id']] else False):
            Logger('* bookmark \"%s | %s\" already in your bookmarks' %(video_info['id'], video_info['title']), kind='Info')
            Logger('*' * 80)

            return MessageContainer('Warning',
                '\"%s | %s\" is already in your bookmarks.' %(video_info['id'], video_info['title']))
        else:
            temp = {}
            temp.setdefault(genre, bm[genre]).append(new_bookmark)
            Dict['Bookmarks'][genre] = temp[genre]
            Logger('* bookmark \"%s | %s\" has been appended to your %s bookmarks' %(video_info['id'], video_info['title'], genre), kind='Info')
            Logger('*' * 80)
            Dict.Save()

            return MessageContainer('Bookmarks',
                '\"%s | %s\" has been added to your bookmarks.' %(video_info['id'], video_info['title']))
    else:
        Dict['Bookmarks'].update({genre: [new_bookmark]})
        Dict.Save()

        return MessageContainer('Bookmarks',
            '\"%s | %s\" has been added to your bookmarks.' %(video_info['id'], video_info['title']))

####################################################################################################
@route(PREFIX + '/removebookmark', video_info=dict)
def RemoveBookmark(video_info):
    """
    Remove Bookmark from Bookmark Dictionary
    If Bookmark to remove is the last Bookmark in the Dictionary,
    then Remove the Bookmark Dictionary also
    """
    genre = video_info['genres'][0] if video_info['genres'] else 'Unknown'
    bm = Dict['Bookmarks']

    if ((True if [b['id'] for b in bm[genre] if b['id'] == video_info['id']] else False) if genre in bm.keys() else False) if bm else False:
        bm_g = bm[genre]
        Logger('*' * 80)
        for i in xrange(len(bm_g)):
            if bm_g[i]['id'] == video_info['id']:
                bm_g.pop(i)
                Dict.Save()
                Logger('* \"%s | %s\" has been removed from Bookmark List'
                    %(video_info['id'], video_info['title']), kind='Info'
                    )
                break

        if len(bm_g) == 0:
            Logger('* \"%s | %s\" bookmark was the last, so removed %s bookmark section'
                %(video_info['id'], video_info['title'], genre), force=True
                )
            Logger('*' * 80)
            del bm_g
            Dict.Save()

            return MessageContainer('Remove Bookmark',
                '\"%s | %s\" bookmark was the last, so removed %s bookmark section'
                %(video_info['id'], video_info['title'], genre)
                )
        else:
            return MessageContainer('Remove Bookmark',
                '\"%s | %s\" has been removed from your bookmarks.'
                %(video_info['id'], video_info['title'])
                )
    else:
        return MessageContainer(
            'Bookmark Error',
            'ERROR: \"%s | %s\" cannot be removed. The Bookmark Dictionary %s does not exist!'
            %(video_info['id'], video_info['title'], genre)
            )

####################################################################################################
@route(PREFIX + '/logger', force=bool)
def Logger(message, force=False, kind=None):
    """Setup logging options based on prefs, indirect because it has no return"""

    if force or Prefs['debug']:
        if kind == 'Debug' or kind == None:
            Log.Debug(message)
        elif kind == 'Info':
            Log.Info(message)
        elif kind == 'Warn':
            Log.Warn(message)
        elif kind == 'Error':
            Log.Error(message)
        elif kind == 'Critical':
            Log.Critical(message)
        else:
            pass
    return
