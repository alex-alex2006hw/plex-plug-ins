######################################################################################
#
#	View47.com - v0.10
#
######################################################################################

TITLE = "View 47"
PREFIX = "/video/view47"
ART = "art-default.jpg"
ICON = "icon-default.png"
ICON_LIST = "icon-list.png"
ICON_COVER = "icon-cover.png"
ICON_SEARCH = "icon-search.png"
ICON_NEXT = "icon-next.png"
ICON_MOVIES = "icon-movies.png"
ICON_SERIES = "icon-tv.png"
ICON_CINEMA = "icon-cinema.png"
ICON_QUEUE = "icon-queue.png"
BASE_URL = "http://view47.com"
MOVIES_URL = "http://view47.com/list/"
SEARCH_URL = "http://view47.com/search/"

import updater, os, sys
from lxml import html
try:
	path = os.getcwd().split("?\\")[1].split('Plug-in Support')[0]+"Plug-ins/View47.bundle/Contents/Code/Modules/View47"
except:
	path = os.getcwd().split("Plug-in Support")[0]+"Plug-ins/View47.bundle/Contents/Code/Modules/View47"
if path not in sys.path:
	sys.path.append(path)

updater.init(repo = '/jwsolve/view47.bundle', branch = 'master')

import cfscrape
scraper = cfscrape.create_scraper()

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
	HTTP.Headers['Referer'] = 'http://view47.me/'
	
######################################################################################
# Menu hierarchy

@handler(PREFIX, TITLE, art=ART, thumb=ICON)
def MainMenu():

	oc = ObjectContainer()
	updater.add_button_to(oc, PerformUpdate)
	oc.add(DirectoryObject(key = Callback(ShowCategory, title="New Movies", category="new-movies.html", page_count = 1), title = "New Movies", thumb = R(ICON_MOVIES)))
	oc.add(DirectoryObject(key = Callback(ShowCategory, title="Cinema Movies", category="cinema-movies.html", page_count = 1), title = "Cinema Movies", thumb = R(ICON_CINEMA)))
	oc.add(DirectoryObject(key = Callback(ShowCategory, title="Movies", category="single-movies.html", page_count = 1), title = "Movies", thumb = R(ICON_MOVIES)))
	oc.add(DirectoryObject(key = Callback(ShowCategory, title="TV Series", category="series-movies.html", page_count = 1), title = "TV Series", thumb = R(ICON_SERIES)))

	oc.add(InputDirectoryObject(key = Callback(Search), title='Search', summary='Search View47', prompt='Search for...'))
	return oc

######################################################################################
@route(PREFIX + "/performupdate")
def PerformUpdate():
	return updater.PerformUpdate()

######################################################################################
# Creates page url from category and creates objects from that page

@route(PREFIX + "/showcategory")	
def ShowCategory(title, category, page_count):

	oc = ObjectContainer(title1 = title)
	if page_count == "1":
		try:
			page = scraper.get(str(category))
			page_data = html.fromstring(page.text)
		except:
			page = scraper.get(MOVIES_URL + str(category))
			page_data = html.fromstring(page.text)
	else:
		try:
			page = scraper.get(str(category) + '?p=' + str(page_count) + '/')
			page_data = html.fromstring(page.text)
		except:
			page = scraper.get(MOVIES_URL + str(category) + '?p=' + str(page_count) + '/')
			page_data = html.fromstring(page.text)
	for each in page_data.xpath("//div[contains(@rel,'items-')]"):
		url = each.xpath("./a/@href")[0]
		title = each.xpath("./a/@title")[0]
		thumb = each.xpath("./img/@src")[0]
		
		if 'Season' in title or 'S0' in title:
			oc.add(DirectoryObject(
				key = Callback(ShowEpisodes, title = title, url = url),
				title = title,
				thumb = thumb
				)
			)
		else:
			oc.add(DirectoryObject(
				key = Callback(EpisodeDetail, title = title, url = url),
				title = title,
				thumb = thumb
				)
			)

	oc.add(NextPageObject(
		key = Callback(ShowCategory, title = category, category = category, page_count = int(page_count) + 1),
		title = "More...",
		thumb = R(ICON_NEXT)
			)
		)
	
	return oc

######################################################################################
# Creates page url from tv episodes and creates objects from that page

@route(PREFIX + "/showepisodes")	
def ShowEpisodes(title, url):

	oc = ObjectContainer(title1 = title)
	page = scraper.get(url)
	page_data = html.fromstring(page.text)
	thumb = page_data.xpath("//div[@class='poster']/a/img/@src")
	for each in page_data.xpath("//div[@class='episode']/a"):
		url = each.xpath("./@href")[0]
		title = each.xpath("./@title")[0]

		oc.add(DirectoryObject(
			key = Callback(EpisodeDetail, title = title, url = url),
			title = title,
			thumb = Resource.ContentsOfURLWithFallback(url = thumb, fallback='icon-cover.png')
			)
		)
	
	return oc

######################################################################################
# Gets metadata and google docs link from episode page. Checks for trailer availablity.

@route(PREFIX + "/episodedetail")
def EpisodeDetail(title, url):
	
	oc = ObjectContainer(title1 = title)
	page = scraper.get(url)
	page_data = html.fromstring(page.text)
	title = page_data.xpath("//meta[@property='og:title']/@content")[0]

	try:
		description = page_data.xpath("//div[@class='info-txt']/p/text()")[0]
	except:
		description = page_data.xpath("//meta[@property='og:description']/@content")[0]
	thumb = page_data.xpath("//div[@class='poster']/a/img/@src")[0]
	director = page_data.xpath("//dl[1]/dd[1]/a/text()")
	imdb_rating = page_data.xpath("//dl[2]/dd[4]/text()")[0]
	
	oc.add(VideoClipObject(
		title = title,
		summary = description,
		directors = director,
		thumb = thumb,
		url = url
		)
	)	
	
	return oc	

####################################################################################################
@route(PREFIX + "/search")
def Search(query):

	oc = ObjectContainer(title2='Search Results')
	searchdata = scraper.get(SEARCH_URL + '%s' % String.Quote(query, usePlus=True) + '.html')

	pagehtml = html.fromstring(searchdata.text)

	for movie in pagehtml.xpath("//ul[@class='list zzz ip_tip']/li"):
		url = movie.xpath("./div/p/a/@href")[0]
		title = movie.xpath("./div/p/a/@title")[0]
		thumb = url

		if 'Season' in title:
			oc.add(DirectoryObject(
				key = Callback(ShowEpisodes, title = title, url = url),
				title = title,
				thumb = Resource.ContentsOfURLWithFallback(url = thumb, fallback='icon-series.png')
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
