FEATURE_PREFIX = '%s/favorites' % consts.prefix

import generic
import downloads

@route(FEATURE_PREFIX)
def MainMenu(refresh = 0, new_episodes = False):
    container = container_for('heading.favorites')
    import re

    if 'favorites' in Dict:
        container.add(button('favorites.heading.migrate', Migrate1to2))
    else:
        recents = bridge.favorite.recents()

        for endpoint, fav in ss.util.sorted_by_title(bridge.favorite.collection().iteritems(), lambda x: x[1]['title']):
            title = fav['title']

            if bridge.favorite.show_has_new_episodes(endpoint, recents):
                new_episodes = True

            if not bridge.settings.get('show_only_new') and bridge.favorite.show_has_new_episodes(endpoint, recents):
                if 'Roku' == Client.Platform:
                    title = F('roku.flag-new-content', title)
                else:
                    title = F('generic.flag-new-content', title)

            overview = fav.get('overview')
            if 'Roku' == Client.Platform and overview:
                overview = re.sub('(19|20)\d\d[-](0[1-9]|1[012])[-](0[1-9]|[12][0-9]|3[01])\s', '', overview).replace(u'\u2014 ','')

            native = TVShowObject(
                rating_key = endpoint,
                title      = title,
                summary    = overview,
                thumb      = fav['artwork'],
                key        = Callback(generic.ListTVShow, refresh = 0, endpoint = endpoint, show_title = title)
            )

            if bridge.settings.get('show_only_new') and bridge.favorite.show_has_new_episodes(endpoint, recents):
                container.add(native)

            if not bridge.settings.get('show_only_new'):
                container.add(native)

        if new_episodes:
            native = button('Watch Later New Episodes', WatchLaterReleases,
            icon       = 'icon-downloads-queue.png'
            )
            container.add(native)
        add_refresh_to(container, refresh, MainMenu)

    return container

@route('%s/WatchLaterReleases' % consts.prefix)
def WatchLaterReleases(refresh = 0, addedqueue = 0, noref = 0):

    recents = bridge.favorite.recents()

    for endpoint, fav in ss.util.sorted_by_title(bridge.favorite.collection().iteritems(), lambda x: x[1]['title']):
        title = fav['title']

        native = TVShowObject(
            rating_key = endpoint,
            title      = title,
            summary    = fav.get('overview'),
            thumb      = fav['artwork'],
            key        = Callback(generic.ListTVShow, refresh = 0, endpoint = endpoint, show_title = title)
        )

        if bridge.favorite.show_has_new_episodes(endpoint, recents):
            listings_endpoint = ss.util.listings_endpoint(endpoint + '/episodes')
            response = JSON.ObjectFromURL(listings_endpoint, cacheTime = 120, timeout = 45)

            items = response.get('items', [])
            allendpoints = [[],[],[]]
            download_ref = 0

            for i, element in enumerate(items):
                permalink        = element.get('endpoint')
                display_title    = element.get('display_title')    or element.get('title')
                element_type     = element.get('_type')
                media_hint       = element_type
                if 'episode' == media_hint: media_hint = 'show'
                if 'episode' == element_type:
                    allendpoints[0].append(permalink)
                    allendpoints[1].append(media_hint)
                    allendpoints[2].append(display_title)

                if 'endpoint' == element_type:
                    Slistings_endpoint = ss.util.listings_endpoint(permalink)
                    Sresponse = JSON.ObjectFromURL(Slistings_endpoint, cacheTime = 120, timeout = 45)
                    Sitems = Sresponse.get('items', [])

                    for j, Selement in enumerate(Sitems):
                        Spermalink        = Selement.get('endpoint')
                        Sdisplay_title    = Selement.get('display_title')    or Selement.get('title')
                        Selement_type     = Selement.get('_type')
                        Smedia_hint = Selement_type
                        if 'episode' == Smedia_hint: Smedia_hint = 'show'
                        if 'episode' == Selement_type:
                            allendpoints[0].append(Spermalink)
                            allendpoints[1].append(Smedia_hint)
                            allendpoints[2].append(Sdisplay_title)

            for i, item in enumerate(allendpoints[0]):
                 if bridge.download.includes(item):
                     b = int(item[item.rfind('/')+1::])
                     if b > download_ref: download_ref = b

            if download_ref:

                bridge.favorite.touch_last_viewed(endpoint)
                for i, item in enumerate(allendpoints[0]):
                     if int(item[item.rfind('/')+1::]) > download_ref:
                         if not bridge.download.includes(item):
                             downloads.Queue(allendpoints[0][i], allendpoints[1][i], allendpoints[2][i])
                             addedqueue = addedqueue + 1
            else:
                noref =  noref + 1

    if addedqueue:
        messagetext = unicode(addedqueue) + ' items added to queue.'
    else:
        messagetext = 'Nothing added to queue.'

    if noref:
       messagetext = messagetext + ' ' + unicode(noref) + ' items need manual queuing.'

    return dialog('heading.download', messagetext)

@route('%s/toggle' % FEATURE_PREFIX)
def Toggle(endpoint, show_title, overview, artwork):
    message = None

    if bridge.favorite.includes(endpoint):
        slog.info('Removing %s from favorites' % show_title)
        message = 'favorites.response.removed'
        bridge.favorite.remove(endpoint)
    else:
        slog.info('Adding %s from favorites' % show_title)
        message = 'favorites.response.added'
        bridge.favorite.append(endpoint = endpoint,
                title = show_title,
                overview = overview,
                artwork = artwork)

    return dialog('heading.favorites', F(message, show_title))

@route('%s/sync' % FEATURE_PREFIX)
def Sync():
    @thread
    def perform_sync(): bridge.favorite.sync()

    perform_sync()
    return dialog('heading.favorites', 'favorites.response.sync')

@route('%s/migrate-1-2' % FEATURE_PREFIX)
def Migrate1to2():
    @thread
    def migrate():
        if 'favorites' in Dict:
            old_favorites = bridge.plex.user_dict()['favorites']
            new_favorites = bridge.favorite.collection()

            for endpoint, title in old_favorites.iteritems():
                if endpoint not in new_favorites:
                    try:
                        response = JSON.ObjectFromURL(ss.util.listings_endpoint(endpoint))
                        bridge.favorite.append(endpoint = endpoint, title = response['display_title'], artwork = response['artwork'])
                    except Exception, e:
                        #util.print_exception(e)
                        pass

            del Dict['favorites']
            bridge.plex.user_dict().Save()

    migrate()
    return dialog('Favorites', 'Your favorites are being updated. Return shortly.')


