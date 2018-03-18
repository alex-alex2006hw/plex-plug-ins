######################################################################################
#
#	Uflix.me - v0.10
#
######################################################################################

TITLE = "UFlix"
PREFIX = "/video/uflix"
ART = "art-default.jpg"
ICON = "icon-default.png"
ICON_LIST = "icon-list.png"
ICON_COVER = "icon-cover.png"
ICON_SEARCH = "icon-search.png"
ICON_NEXT = "icon-next.png"
ICON_MOVIES = "icon-movies.png"
ICON_SERIES = "icon-series.png"
ICON_QUEUE = "icon-queue.png"
BASE_URL = "http://uflix.ws"
MOVIES_URL = "http://uflix.ws/movies"
SHOWS_URL = "http://uflix.ws/tv-shows"
SEARCH_URL = "http://uflix.ws/index.php?menu=search&query="

import updater
updater.init(repo = '/jwsolve/uflix.bundle', branch = 'master')

######################################################################################
# Set global variables

def Start():

	ObjectContainer.title1 = TITLE
	ObjectContainer.art = R(ART)
	DirectoryObject.thumb = R(ICON_LIST)
	DirectoryObject.art = R(ART)
	VideoClipObject.thumb = R(ICON_MOVIES)
	VideoClipObject.art = R(ART)
	
	HTTP.CacheTime = CACHE_1HOUR
	HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36'
	HTTP.Headers['Referer'] = 'http://uflix.ws/'
	
######################################################################################
# Menu hierarchy

@handler(PREFIX, TITLE, art=ART, thumb=ICON)
def MainMenu():

	oc = ObjectContainer()
	updater.add_button_to(oc, PerformUpdate)
	oc.add(InputDirectoryObject(key = Callback(Search), title='Search', summary='Search UFlix', prompt='Search for...'))
	oc.add(DirectoryObject(key = Callback(ShowGenres, title="Movies", listtype='/movies'), title = "Movies", thumb = R(ICON_MOVIES)))
	oc.add(DirectoryObject(key = Callback(ShowGenres, title="TV Shows", listtype='/tv-shows'), title = "TV Shows", thumb = R(ICON_MOVIES)))

	return oc

######################################################################################
@route(PREFIX + "/performupdate")
def PerformUpdate():
	return updater.PerformUpdate()

######################################################################################
# Creates page url from category and creates objects from that page

@route(PREFIX + "/showgenres")	
def ShowGenres(title, listtype):

	oc = ObjectContainer(title1 = title)
	oc.add(InputDirectoryObject(key = Callback(Search), title='Search', summary='Search UFlix', prompt='Search for...'))
	html = HTML.ElementFromURL(BASE_URL + listtype)
	for each in html.xpath("//div[@class='form-group']/select/option"):
		try:
			title = each.xpath("./text()")[0]
			url = each.xpath("./@value")[0]
			oc.add(DirectoryObject(
				key = Callback(ShowCategory, 
					title=title, 
					category=url, 
					page_count = 1), 
				title = title, 
				thumb = R(ICON_MOVIES)
				)
			)
		except:
			pass

	return oc

######################################################################################
# Creates page url from category and creates objects from that page

@route(PREFIX + "/showcategory")	
def ShowCategory(title, category, page_count):

	oc = ObjectContainer(title1 = title)
	oc.add(InputDirectoryObject(key = Callback(Search), title='Search', summary='Search UFlix', prompt='Search for...'))
	thistitle = title
	page_data = HTML.ElementFromURL(BASE_URL + '/' + str(category) + '/date/' + str(page_count))
	
	for each in page_data.xpath("//figure[@style='display:inline-block;']"):
		url = each.xpath("./a/@href")[0]
		title = each.xpath("./a/@title")[0].replace('Watch ','',-1).replace(' Online For FREE','',-1)
		thumb = each.xpath("./a/img/@src")[0]

		if "show" in url:
			oc.add(DirectoryObject(
				key = Callback(ShowEpisodes, title = title, url = url),
				title = title,
				thumb = Resource.ContentsOfURLWithFallback(url = thumb, fallback='icon-cover.png')
				)
			)
		else:
			oc.add(DirectoryObject(
				key = Callback(EpisodeDetail, title = title, url = url),
				title = title,
				thumb = Resource.ContentsOfURLWithFallback(url = thumb, fallback='icon-cover.png')
				)
			)

	oc.add(NextPageObject(
		key = Callback(ShowCategory, title = thistitle, category = category, page_count = int(page_count) + 1),
		title = "More...",
		thumb = R(ICON_NEXT)
			)
		)
	
	return oc

######################################################################################
@route(PREFIX + "/showepisodes")	
def ShowEpisodes(title, url):

	oc = ObjectContainer(title1 = title)
	oc.add(InputDirectoryObject(key = Callback(Search), title='Search', summary='Search UFlix', prompt='Search for...'))
	html = HTML.ElementFromURL(url)
	thumb = html.xpath("//img[@class='img-responsive']/@src")[0]
	for each in html.xpath("//div[@class='col-md-6 col-xs-12']"):
		title = each.xpath("./div[@class='bordered-heading']/span/text()")[0]
		for row in each.xpath("./div[@style='border-bottom:1px solid #C5C5C5;']/a"):
			title = title + ' ' + row.xpath("./text()")[0] + ' ' + row.xpath("./span/text()")[0]
			url = row.xpath("./@href")[0]
			oc.add(DirectoryObject(
				key = Callback(EpisodeDetail, title = title, url = url),
					title = title,
					thumb = Resource.ContentsOfURLWithFallback(url = thumb, fallback='icon-series.png')
					)
			)
			title = each.xpath("./div[@class='bordered-heading']/span/text()")[0]
	return oc

######################################################################################
# Gets metadata and google docs link from episode page. Checks for trailer availablity.

@route(PREFIX + "/episodedetail")
def EpisodeDetail(title, url):
	
	oc = ObjectContainer(title1 = title)
	page_data = HTML.ElementFromURL(url)
	title = page_data.xpath("//div[@class='row title-info']/span/a/text()")[0]
	thumb = page_data.xpath("//img[@class='img-responsive']/@src")[0]
	description = page_data.xpath("//div[@class='row title-plot']/text()")[0]
	
	oc.add(VideoClipObject(
		url = url,
		title = title,
		summary = description,
		thumb = Resource.ContentsOfURLWithFallback(url = thumb, fallback='icon-cover.png')
		)
	)	
	
	return oc	

####################################################################################################
@route(PREFIX + "/search")
def Search(query):

	oc = ObjectContainer(title2='Search Results')
	data = HTTP.Request(SEARCH_URL + '%s' % String.Quote(query, usePlus=True), headers="").content

	html = HTML.ElementFromString(data)

	for each in html.xpath("//figure[@style='display:inline-block;']"):
		url = each.xpath("./a/@href")[0]
		title = each.xpath("./a/@title")[0].replace('Watch ','',-1).replace(' Online For FREE','',-1)
		thumb = each.xpath("./a/img/@src")[0]
		if "show" in url:
			oc.add(DirectoryObject(
				key = Callback(ShowEpisodes, title = title, url = url),
				title = title,
				thumb = Resource.ContentsOfURLWithFallback(url = thumb, fallback='icon-cover.png')
				)
			)
		else:
			oc.add(DirectoryObject(
				key = Callback(EpisodeDetail, title = title, url = url),
				title = title,
				thumb = Resource.ContentsOfURLWithFallback(url = thumb, fallback='icon-cover.png')
				)
			)

	return oc