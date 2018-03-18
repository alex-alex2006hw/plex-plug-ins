# -*- coding: utf-8 -*
VERSION = "1"

# URLs
URL_SITE = "http://www.bringthepopcorn.net"
PLEX_URL = URL_SITE+"/plex"

TITLE = 'BringThePopcorn'
PREFIX = '/video/bringthepopcorn'

TEXT_ALL_MOVIES = u'All Movies'
TEXT_POPULAR_TODAY = u'Popular today'
TEXT_POPULAR_WEEK = u'Popular this week'
TEXT_BEST_SCORE = u'Best rating'
TEXT_NEWLY_ADDED = u'Newly added'
TEXT_SEARCH_SHOW = u'Search'

ART = 'art-default.jpg'
ICON = 'icon-default.png'
NO_POSTER = 'no-poster.jpg'


# Initializer called by the framework
# - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def Start():
    ObjectContainer.title1 = TITLE
    ObjectContainer.art = R( ART )

    DirectoryObject.thumb = R( ICON )
    DirectoryObject.art = R( ART )
    EpisodeObject.thumb = R( ICON )
    EpisodeObject.art = R( ART )
    VideoClipObject.thumb = R( ICON )
    VideoClipObject.art = R( ART )

    HTTP.CacheTime = 600


# Menu builder methods
# - - - - - - - - - - - - - - - - - - - - - - - - - - - -
@handler( PREFIX, TITLE, art=ART, thumb=ICON )
def MainMenu():
    oc = ObjectContainer( )

    #All movies
    oc.add( DirectoryObject( key=Callback( AllMovies, title=TEXT_ALL_MOVIES ),
                             title=TEXT_ALL_MOVIES,
                             thumb=R( ICON ) ) )
    #Popular today
    oc.add( DirectoryObject( key=Callback( PopularToday, title=TEXT_POPULAR_TODAY ),
                             title=TEXT_POPULAR_TODAY,
                             thumb=R( ICON ) ) )
    #Popular this week
    oc.add( DirectoryObject( key=Callback( PopularWeek, title=TEXT_POPULAR_WEEK ),
                             title=TEXT_POPULAR_WEEK,
                             thumb=R( ICON ) ) )
    #Newly added
    oc.add( DirectoryObject( key=Callback( NewlyAdded, title=TEXT_NEWLY_ADDED ),
                             title=TEXT_NEWLY_ADDED,
                             thumb=R( ICON ) ) )
    # #Best rating
    oc.add( DirectoryObject( key=Callback( BestRating, title=TEXT_BEST_SCORE ),
                             title=TEXT_BEST_SCORE,
                             thumb=R( ICON ) ) )
    #Search
    oc.add( InputDirectoryObject( key=Callback( Search ), title=TEXT_SEARCH_SHOW, prompt=TEXT_SEARCH_SHOW ) )

    return oc

@route( PREFIX+'/search' )
def Search(query):
    oc = ObjectContainer( title2=TEXT_SEARCH_SHOW+' results for "'+query+'"' )
    query = query.replace( ' ', '+' )

    for movie in getMoviesFromJsonURL( PLEX_URL+'?search=%s'%query, Search, query ):
        oc.add( movie )

    return oc

@route( PREFIX+'/all' )
def AllMovies(title, page=1):
    oc = ObjectContainer( title2=title )

    for movie in getMoviesFromJsonURL( PLEX_URL+'?p=%s'%page, AllMovies ):
        oc.add( movie )

    oc.objects.sort( key=lambda obj: obj.title )
    return oc


@route( PREFIX+'/new' )
def NewlyAdded(title, page=1):
    oc = ObjectContainer( title2=title )

    for movie in getMoviesFromJsonURL( PLEX_URL+'?o=-created&p=%s'%page, NewlyAdded ):
        oc.add( movie )
    return oc

@route( PREFIX+'/bestrating' )
def BestRating(title, page=1):
    oc = ObjectContainer( title2=title )
    for movie in getMoviesFromJsonURL( PLEX_URL+'?o=-rating&p=%s'%page, BestRating ):
        oc.add( movie )
    return oc

@route( PREFIX+'/popular/today' )
def PopularToday(title, page=1):
    oc = ObjectContainer( title2=title )
    for movie in getMoviesFromJsonURL( PLEX_URL+'?o=-popularity_day&p=%s'%page, PopularToday ):
        oc.add( movie )
    return oc

@route( PREFIX+'/popular/week' )
def PopularWeek(title, page=1):
    oc = ObjectContainer( title2=title )
    for movie in getMoviesFromJsonURL( PLEX_URL+'?o=-popularity_week&p=%s'%page, PopularWeek ):
        oc.add( movie )
    return oc

def NextPage(type, page):
    start = (page-1)*25
    end = start+25
    if type==AllMovies:
        title = TEXT_ALL_MOVIES
    elif type==NewlyAdded:
        title = TEXT_NEWLY_ADDED
    elif type==BestRating:
        title = TEXT_BEST_SCORE
    elif type==PopularToday:
        title = TEXT_POPULAR_TODAY
    elif type==PopularWeek:
        title = TEXT_POPULAR_WEEK
    else:
        title = ''
    return DirectoryObject( key=Callback( type, title="%s (%s-%s)"%(title, start, end), page=page ),
                            title='More results...',
                            thumb=R( ICON ) )

def getMoviesFromJsonURL(url, type, query=None):
    movies = []
    json = JSON.ObjectFromURL( url )
    base_url = json.get( 'base_url', None )

    for item in json.get( 'items', [] ):
        id = item.get( 'id', None )
        title = item.get( 't', None )
        summary = item.get( 's', None )
        year = item.get( 'y', None )
        genre_str = item.get( 'g', [] )
        genres = []
        if genre_str:
            genres = genre_str.split(',')

        duration = item.get( 'd', None )
        if duration:
            duration = int( duration )*60*1000 #duration is in milliseconds
        tagline = item.get( 'tl', None )

        poster = item.get( 'p', None )
        if poster:
            thumb = '%s%s'%(base_url, poster)
        else:
            thumb = R( NO_POSTER )
        backdrop = item.get( 'b', None )
        if backdrop:
            art = '%s%s'%(base_url, backdrop)
        else:
            art = R( ART )

        if id:
            movie = MovieObject(
                url='http://www.youtube.com/watch?v=%s'%id,
                title=title,
                summary=summary
            )
            movie.duration = duration
            movie.year = year
            movie.tagline = tagline
            movie.genres = genres

            movie.thumb = thumb
            movie.art = art
            movies.append( movie )

    next_page = json.get( 'page_next', None )
    if next_page and not query:
        movies.append( NextPage( type, next_page ) )

    return movies














