TITLE  = 'Live Leak'
ART    = 'art-default.jpg'
ICON   = 'icon-default.png'
SEARCH = 'search.png'
PREFIX = '/video/liveleak'

BASE_URL        = "http://www.liveleak.com/"
ITEMS_PER_PAGE  = 12
HTTP_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_5) AppleWebKit/536.30.1 (KHTML, like Gecko) Version/6.0.5 Safari/536.30.1"

PREDEFINED_CATEGORIES = [ 
    {
        'title':    'Recent Items',
        'url':      BASE_URL + 'browse'
    }
]

##########################################################################################
def Start():
    ObjectContainer.title1 = TITLE
    ObjectContainer.art    = R(ART)
    
    DirectoryObject.thumb = R(ICON)

    HTTP.CacheTime             = CACHE_1MINUTE
    HTTP.Headers['User-agent'] = HTTP_USER_AGENT

##########################################################################################
def ValidatePrefs():
    oc = ObjectContainer()
    oc.header  = "Note!"
    oc.message = "Please restart channel for changes to take effect"
    return oc

##########################################################################################
@handler(PREFIX, TITLE, thumb = ICON, art = ART)
def MainMenu():
    oc = ObjectContainer()
    
    pageElement = HTML.ElementFromURL(CreateURL(BASE_URL))
    
    # Add predefined categories
    for category in PREDEFINED_CATEGORIES:
        oc.add(
            DirectoryObject(
                key = 
                    Callback(
                        Videos, 
                        name = category['title'], 
                        url = CreateURL(category['url'])
                    ), 
                title = category['title']
        )
    )
    
    # Add categories parsed from site
    for item in pageElement.xpath("//*[@class = 'nav_bar']//li"):
        url = item.xpath(".//a/@href")[0]
        
        if '/c/' in url:
            title = item.xpath(".//a/text()")[0]
            
            oc.add(
                DirectoryObject(
                    key = 
                        Callback(
                            Videos, 
                            name = title, 
                            url = url
                        ), 
                    title = title
                )
            )       

    title = 'Search...'
    oc.add(
        InputDirectoryObject(
            key = Callback(SearchChoice),
            title = title, 
            prompt = title,
            thumb = R(SEARCH)
        )
    )

    # Add preference for Safe Mode
    oc.add(PrefsObject(title = "Preferences..."))
    
    return oc
    
##########################################################################################
@route(PREFIX + "/Videos", page = int)
def Videos(name, url, page = 1):
    oc = ObjectContainer(title1 = name)

    pageElement = HTML.ElementFromURL(CreateURL(url) + '&page=' + str(page))
    
    for item in pageElement.xpath("//*[contains(@class, 'featured_item_main_outer')]//*[contains(@class,'featured_items_outer')]"):
        try:
            link = item.xpath(".//a/@href")[0]

            if not 'liveleak.com/view' in link:
                continue
                
            title = item.xpath(".//a/@title")[0]
            
            try:
                summary = item.xpath(".//p/text()")[0].strip()
                if not summary:
                    summary = title
            except:
                summary = title
                
            try:
                thumb = item.xpath(".//img/@src")[0]
            except:
                thumb = None
            
            oc.add(
                VideoClipObject(
                    url = link,
                    title = title,
                    summary = summary,
                    thumb = thumb,
                )
            )
            
        except:
            pass
            
    if len(oc) >= ITEMS_PER_PAGE:
        oc.add(
            NextPageObject(
                key = 
                    Callback(
                        Videos,
                        name = name,
                        url = url,
                        page = page + 1
                    ),
                title = "More..."
            )
        )

    if len(oc) < 1:
        oc.header  = "Nothing found"
        oc.message = "No more videos found"

    return oc

###################################################################################################
@route(PREFIX + "/SearchChoice")
def SearchChoice(query):
    oc = ObjectContainer(title2 = 'Sort by')
    
    oc.add(
        DirectoryObject(
            key =
                Callback(
                    Search,
                    query = query,
                    sort = 'relevance'
                ),
            title = 'Sort by Relevance'
        )
    )
    
    oc.add(
        DirectoryObject(
            key =
                Callback(
                    Search,
                    query = query,
                    sort = 'date'
                ),
            title = 'Sort by Date'
        )
    )
    
    oc.add(
        DirectoryObject(
            key =
                Callback(
                    Search,
                    query = query,
                    sort = 'views'
                ),
            title = 'Sort by Views'
        )
    )
    
    oc.add(
        DirectoryObject(
            key =
                Callback(
                    Search,
                    query = query,
                    sort = 'comments'
                ),
            title = 'Sort by Comments'
        )
    )
    
    oc.add(
        DirectoryObject(
            key =
                Callback(
                    Search,
                    query = query,
                    sort = 'votes'
                ),
            title = 'Sort by Votes'
        )
    )
    
    oc.add(
        DirectoryObject(
            key =
                Callback(
                    Search,
                    query = query,
                    sort = 'shared'
                ),
            title = 'Sort by Shared'
        )
    )
    
    return oc

###################################################################################################
@route(PREFIX + "/Search")
def Search(query, sort):
    return Videos(
        name = 'Results for ' + query,
        url = CreateURL(BASE_URL + 'browse?q=%s&sort_by=%s' % (String.Quote(query), sort))
    )

##########################################################################################
def CreateURL(url):
    stringToAdd = ""
    
    if Prefs['safe'] and not 'safe_mode=on' in url:
        url         = url.replace('safe_mode=off', '')
        stringToAdd = 'safe_mode=on'
        
    elif not Prefs['safe'] and not 'safe_mode=off' in url:
        url         = url.replace('safe_mode=on', '')
        stringToAdd = 'safe_mode=off'
        
    if stringToAdd:
        if not '?' in url:
            url = url + '?'
        else:
            url = url + '&'
        
        url = url + stringToAdd     
    
    return url
