######################################################################################
#
#	XMovies8.tv - v0.01
#
######################################################################################

TITLE = "XMovies8"
PREFIX = "/video/xmovies8"
ART = "art-default.jpg"
ICON = "icon-default.png"
ICON_LIST = "icon-list.png"
ICON_COVER = "icon-cover.png"
ICON_SEARCH = "icon-search.png"
ICON_NEXT = "icon-next.png"
ICON_MOVIES = "icon-movies.png"
ICON_SERIES = "icon-series.png"
ICON_QUEUE = "icon-queue.png"
BASE_URL = "http://xmovies8.so"
MOVIES_URL = "http://xmovies8.so"

import os
import sys
from lxml import html
import updater

updater.init(repo = 'jwsolve/xmovies8.bundle', branch = 'master')

try:
	path = os.getcwd().split("?\\")[1].split('Plug-in Support')[0]+"Plug-ins/XMovies8.bundle/Contents/Code/Modules/XMovies8"
except:
	path = os.getcwd().split("Plug-in Support")[0]+"Plug-ins/XMovies8.bundle/Contents/Code/Modules/XMovies8"
if path not in sys.path:
	sys.path.append(path)

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
	
	HTTP.Headers['User-Agent'] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36"
	HTTP.Headers['Referer'] = "xmovies8.so"
	HTTP.Headers['Accept'] = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
	
######################################################################################
# Menu hierarchy

@handler(PREFIX, TITLE, art=ART, thumb=ICON)
def MainMenu():

	oc = ObjectContainer()
	page = scraper.get(BASE_URL)
	page_data = html.fromstring(page.text)
	updater.add_button_to(oc, PerformUpdate)
	oc.add(InputDirectoryObject(key = Callback(Search), title='Search', summary='Search XMovies8', prompt='Search for...'))
	
	for each in page_data.xpath("//ul[contains(@class,'generos')]/li"):
		url = each.xpath("./a/@href")[0]
		title = each.xpath("./a/text()")[0]

		if title != "Animation":
			oc.add(DirectoryObject(
				key = Callback(ShowCategory, title = title, category = url, page_count=1),
				title = title,
				thumb = R(ICON_MOVIES)
				)
			)
	return oc

######################################################################################
@route(PREFIX + "/performupdate")
def PerformUpdate():
	return updater.PerformUpdate()

######################################################################################
@route(PREFIX + "/showcategory")	
def ShowCategory(title, category, page_count):

	oc = ObjectContainer(title1 = title)
	thistitle = title
	thiscategory = category
	oc.add(InputDirectoryObject(key = Callback(Search), title='Search', summary='Search XMovies8', prompt='Search for...'))
	page = scraper.get(str(category) + '/page/' + str(page_count) + '/')
	page_data = html.fromstring(page.text)
	
	for each in page_data.xpath("//div[@class='imagen']"):
		url = each.xpath("./a/@href")[0]
		title = each.xpath("./img/@alt")[0]
		thumb = each.xpath("./img/@src")[0]

		if "Season" in title:
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
		key = Callback(ShowCategory, title = thistitle, category = thiscategory, page_count = int(page_count) + 1),
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
	oc.add(InputDirectoryObject(key = Callback(Search), title='Search', summary='Search XMovies8', prompt='Search for...'))
	page = scraper.get(url)
	page_data = html.fromstring(page.text)
	thumb = page_data.xpath("//div[@class='imgs']/img/@src")[0]
	maintitle = page_data.xpath("//div[@class='dataplus']/h1/text()")[0]
	for each in page_data.xpath("//li[@class='has-sub']/ul/li"):
		url = each.xpath("./a/@href")[0]
		title = maintitle + 'Episode ' + each.xpath("./a/span[@class='datix']/text()")[0]
		oc.add(DirectoryObject(
			key = Callback(EpisodeDetail, title = title, url = url),
			title = title,
			thumb = Resource.ContentsOfURLWithFallback(url = thumb, fallback='icon-cover.png')
			)
		)
	
	return oc

######################################################################################
@route(PREFIX + "/episodedetail")
def EpisodeDetail(title, url):
	
	oc = ObjectContainer(title1 = title)
	oc.add(InputDirectoryObject(key = Callback(Search), title='Search', summary='Search XMovies8', prompt='Search for...'))
	page = scraper.get(url)
	page_data = html.fromstring(page.text)

	title = page_data.xpath("//div[@class='dataplus']/h1/text()")[0]
	description = page_data.xpath("//div[@id='dato-2']/p/text()")[0]
	thumb = page_data.xpath("//div[@class='imgs']/img/@src")[0]
	
	oc.add(VideoClipObject(
		url = url,
		title = title,
		thumb = thumb,
		summary = description
		)
	)	

	return oc

####################################################################################################
@route(PREFIX + "/search")
def Search(query):

	oc = ObjectContainer(title2='Search Results')
	searchdata = scraper.get(BASE_URL + '/?s=%s' % String.Quote(query, usePlus=True))

	pagehtml = html.fromstring(searchdata.text)

	for each in pagehtml.xpath("//div[@class='imagen']"):
		url = each.xpath("./a/@href")[0]
		title = each.xpath("./img/@alt")[0]
		thumb = each.xpath("./img/@src")[0]
		if "Season" in title:
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
				thumb = BASE_URL + thumb
				)
			)

	return oc
