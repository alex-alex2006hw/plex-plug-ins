import downloads
import favorites

@route('%s/RenderListings' % consts.prefix)
def RenderListings(endpoint, default_title = None):
    return render_listings(endpoint, default_title)

@route('%s/WatchOptions' % consts.prefix)
def WatchOptions(endpoint, title, media_hint, summary, thumb, tagline):
    container = render_listings(endpoint, default_title = title,
            cache_time = ss.cache.TIME_DAY)
    container.no_cache = True

    if 'Roku' == Client.Platform:
        wizard_item = VideoClipObject(title = unicode(title), summary = summary, tagline = tagline, art = unicode(thumb),
                url = wizard_url(endpoint), thumb = R('icon-watch-now.png'))
    else:
        wizard_item = VideoClipObject(title = L('media.watch-now'),
            url = wizard_url(endpoint), thumb = R('icon-watch-now.png'))

    sources_item = button('media.all-sources', ListSources,
            endpoint = endpoint, title = title, icon = 'icon-view-all-sources.png')

    if bridge.download.includes(endpoint):
        download_item = button('media.persisted', downloads.OptionsForEndpoint, endpoint = endpoint, icon = 'icon-downloads-queue.png')
    else:
        download_item = button('media.watch-later', downloads.Queue,
            endpoint   = endpoint,
            media_hint = media_hint,
            title      = title,
            icon       = 'icon-downloads-queue.png'
        )

    container.objects.insert(0, wizard_item)
    container.objects.insert(1, download_item)
    container.objects.insert(2, sources_item)

    return container

@route('%s/ListSources' % consts.prefix)
def ListSources(endpoint, title):
    wizard = ss.Wizard(endpoint)
    return render_listings_response(wizard.payload, endpoint, wizard.file_hint)

@route('%s/series/i{refresh}' % consts.prefix)
def ListTVShow(endpoint, show_title, refresh = 0):
    import re

    container, response = render_listings(endpoint + '/episodes', show_title, return_response = True, flags = ['persisted'])
    title_regex         = re.compile(ur'^(.*)'
            + re.escape(response['resource']['display_title'])
            + ur':?\s+', re.UNICODE)

    for item in container.objects:
        md = title_regex.match(item.title)
        if md:
            flags = md.group(1)
            new_title = flags + title_regex.sub('', str(item.title))
            item.title = unicode(new_title)

    labels   = [ 'add', 'remove' ]
    label    = labels[int(bridge.favorite.includes(endpoint))]

    container.objects.insert(0, button('favorites.heading.%s' % label, favorites.Toggle,
        endpoint   = endpoint,
        icon       = 'icon-favorites.png',
        show_title = show_title,
        overview   = (response or {}).get('resource', {}).get('display_overview'),
        artwork    = (response or {}).get('resource', {}).get('artwork')
    ))

    add_refresh_to(container, refresh, ListTVShow,
        endpoint   = endpoint,
        show_title = show_title,
    )

    bridge.favorite.touch_last_viewed(endpoint)

    return container

def render_listings(endpoint, default_title = None, return_response = False,
        cache_time = 120, flags = None, hide_media_prompt = None):

    slog.debug('Rendering listings for %s' % endpoint)
    listings_endpoint = ss.util.listings_endpoint(endpoint)

    if '/shows/latest' in endpoint or '/shows/released' in endpoint or '/shows/letters' in endpoint:
        hide_media_prompt = True

    try:
        response  = JSON.ObjectFromURL(listings_endpoint, cacheTime = cache_time,
                timeout = 45)
        container = render_listings_response(response, endpoint = endpoint,
                default_title = default_title, hide_media_prompt = hide_media_prompt, flags = flags)
    except Exception, e:
        slog.exception('Error requesting %s' % endpoint)

        response  = None
        container = container_for(default_title)
        container.add(button('heading.error', noop))

    if return_response:
        return [ container, response ]
    else:
        return container

def render_listings_response(response, endpoint, default_title = None,
        flags = None, found_media = None, get_media = None, hide_media_prompt = None):
    import re
    oendpoint = endpoint
    display_title = response.get('title') or default_title
    container = container_for(display_title)
    items = response.get('items', [])

    for i, element in enumerate(items):
        native           = None
        permalink        = element.get('endpoint')
        display_title    = element.get('display_title')    or element.get('title')
        overview         = element.get('display_overview') or element.get('overview')
        if 'Roku' == Client.Platform and overview:
            overview = re.sub('(19|20)\d\d[-](0[1-9]|1[012])[-](0[1-9]|[12][0-9]|3[01])\s', '', overview).replace(u'\u2014 ','')
        tagline          = element.get('display_tagline')  or element.get('tagline')
        element_type     = element.get('_type')
        generic_callback = Callback(RenderListings, endpoint = permalink, default_title = display_title)

        if 'endpoint' == element_type:
            native = DirectoryObject(
                title   = display_title,
                tagline = tagline,
                summary = overview,
                key     = generic_callback,
                thumb   = element.get('artwork')
            )

            if '/shows' == permalink:
                native.thumb = R('icon-tv.png')
            elif '/movies' == permalink:
                native.thumb = R('icon-movies.png')

        elif 'show' == element_type:
            if bridge.download.in_history(permalink):
                display_title = F('generic.in-history', display_title)

            native = TVShowObject(
                rating_key = permalink,
                title      = display_title,
                summary    = overview,
                thumb      = element.get('artwork'),
                key        = Callback(ListTVShow, refresh = 0, endpoint = permalink, show_title = display_title)
            )

        elif 'movie' == element_type or 'episode' == element_type:
            media_hint = element_type
            if 'episode' == media_hint:
                media_hint = 'show'
                found_media = True
            if get_media and not bridge.download.includes(permalink):
                downloads.Queue(permalink, media_hint, display_title)
                get_media = get_media + 1

            display_title = flag_title(display_title, permalink, flags = flags)
            display_title = unicode(display_title)

            thumb = element.get('artwork')

            if bridge.settings.get('season_posters') and not thumb:
                trash, subitem = render_listings(endpoint = permalink, return_response = True)
                for j, zelement in enumerate(subitem.get('items', [])):
                     thumb = zelement.get('artwork')

            native = PopupDirectoryObject(
                title   = display_title,
                tagline = tagline,
                thumb   = thumb,
                summary = overview,
                key     = Callback(WatchOptions, endpoint = permalink, title = display_title, media_hint = media_hint, summary = overview, thumb = element.get('artwork'), tagline = tagline)
            )

        elif 'foreign' == element_type:
            native = VideoClipObject(
                title = element['domain'],
                url   = wizard_url(endpoint, i)
            )

        if None != native and not get_media:
            container.add( native )

    if hide_media_prompt:
        found_media = False

    if found_media and not get_media:
        native = button('Download All Content', getallmedia,
            endpoint = oendpoint,
            icon     = 'icon-downloads-queue.png'
        )
        container.objects.insert(0, native)

    if get_media:
         return  unicode(get_media)
    return container

@route('%s/getallmedia' % consts.prefix)
def getallmedia(endpoint, cache_time = 120):
    listings_endpoint = ss.util.listings_endpoint(endpoint)
    response  = JSON.ObjectFromURL(listings_endpoint, cacheTime = cache_time, timeout = 45)
    messagetext = render_listings_response(response, endpoint, get_media = True) + ' items added to queue.'
    return dialog('heading.download', messagetext)

def flag_title(title, endpoint, flags = None):
    flags = flags or ['persisted', 'favorite']

    if 'persisted' in flags and bridge.download.includes(endpoint):
        if 'Roku' == Client.Platform:
            return F('roku.flag-persisted', title)
        else:
            return F('generic.flag-persisted', title)

    if 'favorite' in flags and bridge.favorite.includes(endpoint):
        if 'Roku' == Client.Platform:
            return F('roku.flag-favorite', title)
        else:
            return F('generic.flag-favorite', title)

    return title

def wizard_url(endpoint, index = 0):
    return '//ss/wizard?endpoint=%s&avoid_flv=%s&start_at=%s' % (endpoint,
            int(bridge.settings.get('avoid_flv_streaming', False)), index)

