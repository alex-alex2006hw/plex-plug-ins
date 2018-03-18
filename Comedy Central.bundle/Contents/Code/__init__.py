TITLE = 'Comedy Central'
ART = 'art-default.jpg'
ICON = 'icon-default.jpg'
PREFIX = '/video/comedycentral'

BASE_URL = 'http://www.cc.com'
SHOWS_URL = BASE_URL + '/shows'
TOSH_URL = 'http://tosh.cc.com'
FULL_SPECIALS = BASE_URL + '/shows/stand-up-specials'

# Pull the json from the HTML content to prevent any issues with redirects and/or bad urls
RE_MANIFEST_URL = Regex('var triforceManifestURL = "(.+?)";', Regex.DOTALL)
RE_MANIFEST = Regex('var triforceManifestFeed = (.+?);', Regex.DOTALL)
EXCLUSIONS = ['South Park']
SEARCH ='http://search.cc.com/solr/cc/select?q=%s&wt=json&defType=edismax&start='
SEARCH_TYPE = ['Video', 'Comedians', 'Episode', 'Series']
ENT_LIST = ['ent_m071', 'f1071', 'ent_m013', 'f1013', 'ent_m081', 'ent_m100', 'ent_m150', 'ent_m157', 'ent_m020', 'ent_m160', 'ent_m012']

####################################################################################################
def Start():

    ObjectContainer.title1 = TITLE
    HTTP.CacheTime = CACHE_1HOUR
    HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'

####################################################################################################
@handler(PREFIX, TITLE, art=ART, thumb=ICON)
def MainMenu():

    oc = ObjectContainer()
    oc.add(DirectoryObject(key = Callback(FeedMenu, title="Full Episodes", url=BASE_URL+'/full-episodes'), title = "Full Episodes"))
    oc.add(DirectoryObject(key = Callback(FeedMenu, title="Shows", url=BASE_URL+'/shows'), title = "Shows"))
    oc.add(DirectoryObject(key = Callback(StandupSections, title="Standup"), title = "Standup"))
    oc.add(InputDirectoryObject(key = Callback(SearchSections, title="Search"), title = "Search"))

    return oc

####################################################################################################
@route(PREFIX + '/standupsections')
def StandupSections(title):
    
    oc = ObjectContainer(title2=title)
    oc.add(DirectoryObject(key = Callback(FeedMenu, title="Comedians", url=BASE_URL+"/comedians"), title = "Comedians"))
    oc.add(DirectoryObject(key = Callback(FeedMenu, title="Videos", url=BASE_URL+"/stand-up/video-clips"), title = "Videos"))
    oc.add(DirectoryObject(key = Callback(FeedMenu, title="Full Specials", url=FULL_SPECIALS), title = "Full Specials"))

    return oc

####################################################################################################
# This function pulls the json feeds in the ENT_LIST for any page
@route(PREFIX + '/feedmenu')
def FeedMenu(title, url, thumb=''):

    oc = ObjectContainer(title2=title)
    feed_title = title

    try: content = HTTP.Request(url, cacheTime=CACHE_1DAY).content
    except: return ObjectContainer(header="Incompatible", message="The URL is not valid %s." % (url))
    try:
        zone_list = JSON.ObjectFromString(RE_MANIFEST.search(content).group(1))['manifest']['zones']
    except:
        try: zone_list = JSON.ObjectFromURL(RE_MANIFEST_URL.search(content).group(1))['manifest']['zones']
        except: return ObjectContainer(header="Incompatible", message="Unable to find video feeds for %s." % (url))

    if not thumb:
        try: thumb = HTML.ElementFromString(content).xpath('//meta[@property="og:image"]/@content')[0].strip()
        except: thumb = ''

    for zone in zone_list:

        if zone in ('header', 'footer', 'ads-reporting', 'ENT_M171'):
            continue

        json_feed = zone_list[zone]['feed']

        # Split feed to get ent code
        try: ent_code = json_feed.split('/feeds/')[1].split('/')[0]
        except:
            try: ent_code = json_feed.split('/modules/')[1].split('/')[0]
            except: ent_code = ''

        ent_code = ent_code.split('_cc')[0].split('_tosh')[0]

        if ent_code not in ENT_LIST:
            continue

        result_type = GetType(ent_code)
        json = JSON.ObjectFromURL(json_feed, cacheTime = CACHE_1DAY)

        # Get the title
        # Title for most are under promo/headline
        # full episode main page(ent_m081), individual show video clips(ent_m071, f1071), comedians(ent_m157) and standup specials(ent_m012)
        try: title = json['result']['promo']['headline']
        except:
            # Title for shows(ent_m100 and ent_m150) under data/headerText
            try: title = json['result']['data']['headerText']
            except:
                # Title for individual show full episodes(ent_m013 and f1013) are under promo/headerText
                try: title = json['result']['promo']['headerText']
                except:
                    # Title for playlist (ent_m020) is under plalylist/title
                    try: title = json['result']['playlist']['title']
                    except: title = feed_title

        # Create menu items for those that need to go to Produce Sections
        # ent_m071 and f1071-each show's video clips, ent_m157-comedian lists, and ent_m100 and entm150 - show sections
        if ent_code in ['ent_m071', 'f1071', 'ent_m157'] or (ent_code in [ 'ent_m100', 'ent_m150'] and url==SHOWS_URL):

            if title not in ['You May Also Like', 'Featured Comedians']:

                oc.add(DirectoryObject(
                    key = Callback(ProduceSection, title=title, url=json_feed, result_type=result_type),
                    title = title,
                    thumb = Resource.ContentsOfURLWithFallback(url=thumb)
               ))

        # Create menu for all others to produce videos
        # ent_m013 and f1013 - each show's full episodes, ent_m020-playlists, ent_m160-Standup video clips, and ent_m012-standup specials/related items listing
        elif ent_code in ['ent_m081','ent_m013', 'f1013', 'ent_m020', 'ent_m160', 'ent_m012']:

            # Checck ent_m012/related items for videos before creating a directory
            if ent_code == 'ent_m012':

                example_url = json['result']['relatedItems'][0]['canonicalURL']

                if ('/video-clips/') not in example_url and ('/full-episodes/') not in example_url:
                    continue

            oc.add(DirectoryObject(
                key = Callback(ShowVideos, title=title, url=json_feed, result_type=result_type),
                title = title,
                thumb = Resource.ContentsOfURLWithFallback(url=thumb)
            ))

        # Also create additional menu items for full episode feeds for each show
        if ent_code == 'ent_m081':

            for item in json['result']['shows']:

                try: summary = item['show']['description']
                except: summary = ''
                try: thumb = item['show']['images'][0]['url']
                except: thumb = ''
                oc.add(DirectoryObject(
                    key = Callback(ShowVideos, title=item['show']['title'], url=item['fullEpisodesFeedURL'], result_type='episodes'),
                    title = item['show']['title'],
                    summary = summary,
                    thumb = Resource.ContentsOfURLWithFallback(url=thumb)
                ))

    # Some shows do not have the proper feeds to display videos so we send them to function to find feeds
    if len(oc) < 1 and '/shows/' in url:
        oc.add(DirectoryObject(key = Callback(ShowSections, title=feed_title, url=url, thumb=thumb), title=title, thumb=thumb))

    if len(oc) < 1:
        return ObjectContainer(header="Empty", message="There are no results to list.")
    else:
        return oc

#######################################################################################
# This function pulls the video links from the navigation bar of a show when the FeedMenu function produces no results
@route(PREFIX + '/showsections')
def ShowSections(title, url, thumb=''):
    
    oc = ObjectContainer(title2=title)
    content = HTTP.Request(url, cacheTime=CACHE_1DAY).content
    page = HTML.ElementFromString(content)
        
    if not thumb:
        try: thumb = page.xpath('//meta[@property="og:image"]/@content')[0].strip()
        except: thumb = ''

    # Get the full episode and video clip feeds 
    for section in page.xpath('//ul[@class="show_menu"]/li/a'):
        section_title = section.xpath('./text()')[0].strip().title()
        section_url = section.xpath('./@href')[0]
        if not section_url.startswith('http://'):
            section_url = BASE_URL + section_url
        if 'Episode' in section_title or 'Video' in section_title or 'Sketches' in section_title:
            try: 
               section_content = HTTP.Request(section_url, cacheTime=CACHE_1DAY).content
               feed_list = JSON.ObjectFromURL(RE_MANIFEST_URL.search(section_content).group(1))['manifest']['zones']
            except:
               return ObjectContainer(header="Incompatible", message="Unable to find video feeds for %s." % (url))
            Log('the value of feed_list is %s' %feed_list)
            Log('the value of feed_list[0] is %s' %feed_list[0])
            # There should only be one feed listed for show video pages
            if 'ent_m112' in feed_list[0] or 'ent_m116' in feed_list[0] or 'ent_m228' in feed_list[0]:
                oc.add(DirectoryObject(
                    key=Callback(ProduceSection, title=section_title, url=feed_list[0], result_type='filters', thumb=thumb),
                    title=section_title,
                    thumb = Resource.ContentsOfURLWithFallback(url=thumb)
                ))
        # Create video object for listed special full shows
        elif 'Full Special' in section_title:
            oc.add(VideoClipObject(
                url = section_url, 
                title = section_title, 
                thumb = Resource.ContentsOfURLWithFallback(url=thumb)
            ))

    if len(oc) < 1:
        Log ('still no value for objects')
        return ObjectContainer(header="Empty", message="There are no video sections for this show." )
    else:
        return oc
####################################################################################################
# This function produces sections from a json feeds
# including shows(ent_m100), AtoZ shows(ent_m150), comedians (ent_m157), and video filters(ent_m116)
@route(PREFIX + '/producesection', alpha=int)
def ProduceSection(title, url, result_type='data', thumb='', alpha=None):

    oc = ObjectContainer(title2=title)
    (section_title, feed_url) = (title, url)
    counter=0
    json = JSON.ObjectFromURL(url)

    # Create item lists
    try: 
        # Create list for show feeds (data/items) and comedians (promo/items)
        item_list = json['result'][result_type]['items']
    except: 
        # Create list for video feed filters
        try: item_list = json['result'][result_type]
        except: item_list = []

    # Create list for alphabet sections for the AtoZ show feeds
    if '/ent_m150/' in feed_url and alpha:
        item_list = json['result'][result_type]['items'][alpha]['sortedItems']
    for item in item_list:
        # Produce menu items for show lists
        if '/ent_m150/' in feed_url or '/ent_m100/' in feed_url:
            # Produce alphabetic menu items for AtoZ
            if '/ent_m150/' in feed_url and not alpha:
                oc.add(DirectoryObject(
                    key=Callback(ProduceSection, title=item['letter'], url=feed_url, result_type=result_type, alpha=counter),
                    title=item['letter']
                ))
                counter=counter+1
            # Produce menu items for each show (under Featured, a letter, etc)
            else:
                try: url = item['canonicalURL']
                except:
                    try: url = item['url']
                    except: continue
                # Skip bad show urls that do not include '/shows/' or events. If '/events/' there is no manifest.
                if '/shows/' not in url:
                    continue
                if item['title'] in EXCLUSIONS:
                    continue
                try: thumb = item['image']['url']
                except: thumb = thumb
                if thumb.startswith('//'):
                    thumb = 'https:' + thumb
                oc.add(DirectoryObject(
                    key=Callback(FeedMenu, title=item['title'], url=url, thumb=thumb),
                    title=item['title'],
                    thumb = Resource.ContentsOfURLWithFallback(url=thumb)
                ))
        # Produce menu items for comedians
        elif result_type == 'promo':

            oc.add(DirectoryObject(
                key = Callback(FeedMenu, title=item['name'], url=item['canonicalURL'], thumb=item['image']['url']),
                title = item['name'],
                thumb = Resource.ContentsOfURLWithFallback(url=item['image']['url'])
            ))

        # Produce menu items for video filters for the video clips for an individual a show
        else:
            url = json['result'][result_type][item]

            oc.add(DirectoryObject(
                key = Callback(ShowVideos, title=item, url=url, result_type='videos'),
                title = item,
                thumb = Resource.ContentsOfURLWithFallback(url=thumb)
            ))
    
    if len(oc) < 1:
        Log ('still no value for objects')
        return ObjectContainer(header="Empty", message="There are no results to list right now.")
    else:
        return oc
####################################################################################################
# This function produces the videos listed in a json feed under items
@route(PREFIX + '/showvideos')
def ShowVideos(title, url, result_type):

    oc = ObjectContainer(title2=title)
    json = JSON.ObjectFromURL(url)

    if 'playlist' in result_type:
        videos = json['result'][result_type]['videos']
    else:
        videos = json['result'][result_type]

    for video in videos:

        vid_url = video['canonicalURL']

        # catch any bad links that get sent here
        if not ('/video-clips/') in vid_url and not ('/episodes/') in vid_url and not ('/full-episodes/') in vid_url:
            continue

        try: thumb = video['images'][0]['url']
        except:
            try: thumb = video['image'][0]['url']
            except:  thumb = None
        if thumb and thumb.startswith('//'):
            thumb = 'http:' + thumb

        if result_type == 'relatedItems':

            oc.add(VideoClipObject(
                url = vid_url, 
                title = video['title'], 
                thumb = Resource.ContentsOfURLWithFallback(url=thumb ),
                summary = video['description']
            ))
        else:
            try: show = video['show']['title']
            except: show = video['showTitle']

            try: episode = int(video['season']['episodeNumber'])
            except: episode = None

            try: season = int(video['season']['seasonNumber'])
            except: season = None

            try: raw_date = video['airDate']
            except: raw_date = video['publishDate']
            if raw_date and raw_date.isdigit(): 
                raw_date = Datetime.FromTimestamp(float(raw_date)).strftime('%m/%d/%Y')
            date = Datetime.ParseDate(raw_date)

            # Durations for clips have decimal points
            duration = video['duration']
            if duration:
                if isinstance(duration, int):
                    duration = duration * 1000
                else:
                    try: duration = Datetime.MillisecondsFromString(duration)
                    except: 
                        # Durations for clips have decimal points 
                        try: duration = int(duration.split('.')[0]) * 1000
                        except:  duration = 0

            # Everything else has episode and show info now
            oc.add(EpisodeObject(
                url = vid_url, 
                show = show,
                season = season,
                index = episode,
                title = video['title'], 
                thumb = Resource.ContentsOfURLWithFallback(url=thumb ),
                originally_available_at = date,
                duration = duration,
                summary = video['description']
            ))

    try: next_page = json['result']['nextPageURL']
    except: next_page = None

    if next_page and len(oc) > 0:

        oc.add(NextPageObject(
            key = Callback(ShowVideos, title=title, url=next_page, result_type=result_type),
            title = 'Next Page ...'
        ))

    if len(oc) < 1:
        Log ('still no value for objects')
        return ObjectContainer(header="Empty", message="There are no unlocked videos available to watch.")
    else:
        return oc

####################################################################################################
# This function produces the types of results (show, video, etc) returned from a search
@route(PREFIX + '/searchsections')
def SearchSections(title, query):
    
    oc = ObjectContainer(title2=title)
    json_url = SEARCH %String.Quote(query, usePlus = False)
    local_url = json_url + '0&facet=on&facet.field=bucketName_s'
    json = JSON.ObjectFromURL(local_url)
    i = 0
    search_list = json['facet_counts']['facet_fields']['bucketName_s']
    for item in search_list:
        if item in SEARCH_TYPE and search_list[i+1]!=0:
            oc.add(DirectoryObject(key = Callback(Search, title=item, url=json_url, search_type=item), title = item))
        i=i+1

    return oc
####################################################################################################
# This function produces the results for a search under each search type
@route(PREFIX + '/search', start=int)
def Search(title, url, start=0, search_type=''):

    oc = ObjectContainer(title2=title)
    local_url = '%s%s&fq=bucketName_s:%s' %(url, start, search_type)
    json = JSON.ObjectFromURL(local_url)

    for item in json['response']['docs']:

        result_type = item['bucketName_s']
        title = item['title_t']
        full_title = '%s: %s' % (result_type, title)

        try: item_url = item['url_s']
        except: continue

        # For Shows
        if result_type == 'Series':

            oc.add(DirectoryObject(
                key = Callback(FeedMenu, title=item['title_t'], url=item_url, thumb=item['imageUrl_s']),
                title = full_title,
                thumb = Resource.ContentsOfURLWithFallback(url=item['imageUrl_s'])
            ))

        # For Comedians
        elif result_type == 'Comedians':

            oc.add(DirectoryObject(
                key = Callback(FeedMenu, title=item['title_t'], url=item_url, thumb=item['imageUrl_s']),
                title = full_title,
                thumb = Resource.ContentsOfURLWithFallback(url=item['imageUrl_s'])
            ))

        # For Episodes and ShowVideo(video clips)
        else:
            try: season = int(item['seasonNumber_s'].split(':')[0])
            except: season = None

            try: episode = int(item['episodeNumber_s'])
            except: episode = None

            try: show = item['seriesTitle_t']
            except: show = None

            try: summary = item['description_t']
            except: summary = None

            oc.add(EpisodeObject(
                url = item_url, 
                show = show, 
                title = full_title, 
                thumb = Resource.ContentsOfURLWithFallback(url=item['imageUrl_s']),
                summary = summary, 
                season = season, 
                index = episode, 
                duration = Datetime.MillisecondsFromString(item['duration_s']), 
                originally_available_at = Datetime.ParseDate(item['contentDate_dt'])
            ))

    if json['response']['start']+10 < json['response']['numFound']:

        oc.add(NextPageObject(
            key = Callback(Search, title='Search', url=url, search_type=search_type, start=start+10),
            title = 'Next Page ...'
        ))

    if len(oc) < 1:
        return ObjectContainer(header="Empty", message="There are no results to list.")
    else:
        return oc

####################################################################################################
# This function pulls the related type used for pulls by each ENT feed
@route(PREFIX + '/gettype')
def GetType(ent):

    # ent_m100, ent_m150, and ent_m160 are all of type items
    result_type = 'data'
    ENTTYPE_LIST = [
        {'ent':'ent_m071', 'type':'sortingOptions'},
        {'ent':'f1071', 'type':'sortingOptions'},
        {'ent':'ent_m013', 'type':'episodes'},
        {'ent':'f1013', 'type':'episodes'},
        {'ent':'ent_m081', 'type':'episodes'},
        {'ent':'ent_m157', 'type':'promo'},
        {'ent':'ent_m020', 'type':'playlist'},
        {'ent':'ent_m160', 'type':'items'},
        {'ent':'ent_m012', 'type':'relatedItems'}
    ]

    for item in ENTTYPE_LIST:

        if ent == item['ent']:
            result_type = item['type']
            break

    return result_type
