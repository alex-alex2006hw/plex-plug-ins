import bridge

pref_keys = [
    'avoid_flv_streaming',
    'avoid_flv_downloading',
    'download_limit',
    'download_strategy',
    'simultaneous_downloads',
    'auto_force_success',
    'show_only_new',
    'season_posters'
]

def download_strategy(strategy):
    if 'auto' == strategy:
        strategy = 'curl'

        if 'Linux' == platform_os():
            strategy = 'wget'

    return strategy

def platform_os():
    return Platform.OS

class BridgeSettingsStore(object):
    def __init__(self):
        Dict['access']

    def get(self, key, default = None):
        defined = 'get_%s' % key
        if hasattr(self, defined):
            return getattr(self, defined)()

        if key in pref_keys:
            return Prefs[key]

        if not key in Dict:
            Dict[key] = default

        return Dict[key]

    def set(self, key, value):
        Dict[key] = value

    def clear(self, key):
        if key in Dict:
            del Dict[key]
            Dict.Save()

    def persist(self):
        Dict.Save()

    def get_download_strategy(self):
        return download_strategy(Prefs['download_strategy'])

    def get_show_destination(self):
        return section_destination('show')

    def get_movie_destination(self):
        return section_destination('movie')

def section_destination(section):
    found = section_info(section)
    if not found: return

    return found[1]

def plex_endpoint(path): return 'http://127.0.0.1:32400%s' % path

def section_info(section):
    import re

    xmlobj   = XML.ElementFromURL(plex_endpoint('/library/sections'))
    query    = '//Directory[@type="%s"]' % section
    matching = filter(lambda el: '.none' not in el.get('agent'), xmlobj.xpath(query))

    for directory in matching:
        locations = directory.xpath('./Location')
        for location in locations:
            path = location.get('path')
            if re.search(r'ss.?p', path):
                return match_from(directory, location)
    else:
        return match_from(directory, locations[0])

def match_from(directory, location):
    return [ directory.get('key'), location.get('path') ]

def refresh_section(section):
    found = section_info(section)
    if not found: return

    HTTP.Request(plex_endpoint('/library/sections/%s/refresh' % found[0]), immediate = True)

keepalive_endpoint = '%s/_keepalive' % consts.prefix
keepalive_url = plex_endpoint(keepalive_endpoint)

@route(keepalive_endpoint)
def keepalive():
    Thread.CreateTimer(8, keepalive_request)
    return dialog('shhhh', 'shhhhhhh')

def keepalive_request():
    if bridge.download.assumed_running():
        HTTP.Request(keepalive_url, immediate = True)

dispatch_without_keepalive = bridge.download.dispatch
def dispatch_with_keepalive(*args, **kwargs):
    if not bridge.download.assumed_running():
        keepalive()

    dispatch_without_keepalive(*args, **kwargs)

def init():
    if bridge.settings.store is None:
        Log('bridge init')
        bridge.settings.store = BridgeSettingsStore()
        bridge.download.update_library = refresh_section
        bridge.download.dispatch = dispatch_with_keepalive

    return bridge

