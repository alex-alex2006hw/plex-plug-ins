NAME = 'NBC'
ART = 'art-default.jpg'
ICON = 'icon-default.jpg'
PREFIX = '/video/nbc'

BASE_URL = 'http://www.nbc.com'
# active=1(shows) and published=1(videos) hide shows and videos that currently do not work, entitlement=free hides locked videos, and include=image includes the image URLs in json
SHOWS_URL = 'https://api.nbc.com/v3.14/shows?filter[active]=1&include=image&page[size]=30&sort=sortTitle'
VIDEO_URL = 'https://api.nbc.com/v3.14/videos?filter[entitlement]=free&filter[published]=1&include=image&page[size]=30&sort=-airdate'

# API can be filtered by any field by adding &filter[filter name]=filter value (spaces must be %20)
FILTER = '&filter[%s]=%s'

GENRES = ['Drama', 'Comedy', 'Family and Kids', 'LateNight', 'Reality and Game Show', 'Reality', 'Talk and Interview', 'News and Information', 'Live Events and Specials']

####################################################################################################
def Start():

	try:
		json_obj = JSON.ObjectFromURL('http://ip-api.com/json', cacheTime=10)
	except:
		Log("IP Address Check Failed")
		json_obj = None

	if json_obj and 'countryCode' in json_obj and json_obj['countryCode'] != 'US':
		Log("= WARNING ==========================================================================================")
		Log("  According to your IP address you are not in the United States.")
		Log("  Due to geo-blocking by the content provider, this channel does not work outside the United States.")
		Log("====================================================================================================")

	ObjectContainer.title1 = NAME
	HTTP.CacheTime = CACHE_1HOUR
	HTTP.Headers['User-Agent'] = 'BRNetworking/2.7.0.1449 (iPad;iPhone OS-8.1)'

####################################################################################################
@handler(PREFIX, NAME, art=ART, thumb=ICON)
def MainMenu():

	oc = ObjectContainer()

	oc.add(DirectoryObject(key = Callback(FullEpSections, title="Episodes"), title = "Latest Full Episodes"))
	oc.add(DirectoryObject(key = Callback(ShowSections, title="Shows"), title = "Shows"))

	return oc

####################################################################################################
@route(PREFIX + '/showsections')
def ShowSections(title):

	oc = ObjectContainer(title2=title)

	oc.add(DirectoryObject(key = Callback(ShowList, title="Current Shows", url=SHOWS_URL + FILTER % ('category', 'Current')), title = "Current Shows"))
	oc.add(DirectoryObject(key = Callback(ShowList, title="Classic Shows", url=SHOWS_URL + FILTER % ('category', 'Classic')), title = "Classic Shows"))
	oc.add(DirectoryObject(key = Callback(Genres, title="Shows By Genre", url=SHOWS_URL), title = "Shows By Genre"))
	oc.add(DirectoryObject(key = Callback(ShowList, title="All Shows", url=SHOWS_URL), title = "All Shows"))

	return oc

####################################################################################################
@route(PREFIX + '/fullepsections')
def FullEpSections(title, url=''):

	oc = ObjectContainer(title2=title)

	# Add full episode filter to url
	fullep_url = VIDEO_URL + FILTER % ('type', 'Full%20Episode')

	for day_type in ['Primetime', 'LateNight', 'Daytime', ]:

		day_url = fullep_url + FILTER % ('dayPart', day_type)
		oc.add(DirectoryObject(key = Callback(VideoList, title="%s Episodes" % (day_type), url=day_url), title="%s Episodes" % (day_type)))

	oc.add(DirectoryObject(key = Callback(Genres, title="Full Episodes By Genre", url=fullep_url), title="Full Episodes By Genre"))
	oc.add(DirectoryObject(key = Callback(VideoList, title="All Full Episodes", url=fullep_url), title="All Full Episodes"))

	return oc

####################################################################################################
# Function to produce shows or videos by genre
@route(PREFIX + '/genres')
def Genres(title, url):

	oc = ObjectContainer(title2=title)

	for item in GENRES:

		sort_url = url + FILTER % ('genre', String.Quote(item, usePlus = False))

		if 'Shows' in title:
			# Skip the genre fields that do not work for shows
			if item in ['Family and Kids', 'Talk and Interview']:
				continue
			oc.add(DirectoryObject(
				key = Callback(ShowList, title=item, url=sort_url),
				title = item
			))
		else:
			# Skip the genre fields that do not work for videos
			if item in ['LateNight', 'Reality']:
				continue
			oc.add(DirectoryObject(
				key = Callback(VideoList, title=item, url=sort_url),
				title = item
			))

	return oc

####################################################################################################
@route(PREFIX + '/showlist')
def ShowList(title, url):

	oc = ObjectContainer(title2=title)

	#show_attirbutes = '&fields[shows]=shortTitle,shortDescription'
	json = JSON.ObjectFromURL(url)

	for show in json['data']:

		show_title = show['attributes']['shortTitle']
		summary = String.StripTags(unicode(show['attributes']['shortDescription']))

		thumb_id = show['relationships']['image']['data']['id']
		thumb = GetImage(thumb_id, json)

		show_id = show['id']
		show_url = VIDEO_URL + FILTER %('show', show_id)
		ag_id = show['relationships']['aggregates']['data']['id']

		oc.add(DirectoryObject(
			key = Callback(Aggregates, title=show_title, url=show_url, ag_id=ag_id, thumb=thumb),
			title = show_title,
			summary = summary,
			thumb = Resource.ContentsOfURLWithFallback(thumb, fallback=ICON)
		))

	try: next_page = json['links']['next']
	except: next_page = None
	if next_page:
		oc.add(NextPageObject(
			key = Callback(ShowList, title=title, url=next_page),
			title = 'Next Page ...'
		))

	if len(oc) < 1:
		return ObjectContainer(header="Empty", message="There are no results to list.")
	else:
		return oc

####################################################################################################
# This function pulls the video types from the aggregate json for a show
@route(PREFIX + '/aggregates')
def Aggregates(title, url, ag_id, thumb=''):

	oc = ObjectContainer(title2=title)

	local_url = 'https://api.nbc.com/v3.14/aggregatesShowProperties/' + ag_id
	try: json = JSON.ObjectFromURL(local_url)
	except: return ObjectContainer(header="Invalid URL", message="The URL is invalid or does not contain json.")

	vidtype_list = json['data']['attributes']['videoTypes']

	for item in vidtype_list:

		sort_url = url + FILTER %('type', String.Quote(item, usePlus = False))

		oc.add(DirectoryObject(
			key = Callback(VideoList, title=item, url=sort_url),
			title = item,
			thumb = Resource.ContentsOfURLWithFallback(thumb, fallback=ICON)
		))

	return oc

####################################################################################################
@route(PREFIX + '/videolist')
def VideoList(title, url):

	oc = ObjectContainer(title2=title)

	#video_attributes = '&fields[videos]=title,description,airdate,fullUrl,runTime,episodeNumber,seasonNumber,categories'
	try: json = JSON.ObjectFromURL(url)
	except: return ObjectContainer(header="Invalid URL", message="The URL is invalid or does not contain json.")

	for episode in json['data']:

		vid_url = episode['attributes']['fullUrl']

		date = Datetime.ParseDate(episode['attributes']['airdate'])

		duration = episode['attributes']['runTime']
		duration = int(duration) * 1000

		show_name = '' 
		for item in episode['attributes']['categories']: 
			if item.startswith('Series'):
				show_name = item.split('Series/')[1]
				break

		try: ep_index = int(episode['attributes']['episodeNumber'])
		except: ep_index = None
		try: ep_season = int(episode['attributes']['seasonNumber'])
		except: ep_season = None

		try: 
			thumb_id = episode['relationships']['image']['data']['id']
			thumb = GetImage(thumb_id, json)
		except: thumb = ''

		oc.add(EpisodeObject(
			url = vid_url,
			show = show_name,
			title = episode['attributes']['title'],
			summary = episode['attributes']['description'],
			thumb = Resource.ContentsOfURLWithFallback(url=thumb),
			season = ep_season,
			index = ep_index,
			duration = duration,
			originally_available_at = date
		))

	try: next_page = json['links']['next']
	except: next_page = None
	if next_page:
		oc.add(NextPageObject(
			key = Callback(VideoList, title=title, url=next_page),
			title = 'Next Page ...'
		))

	if len(oc) < 1:
		return ObjectContainer(header="Empty", message="There are no results to list.")
	else:
		return oc

####################################################################################################
# This function pulls the image url from the included image data using the image id for each show or video
@route(PREFIX + '/getimage')
def GetImage(thumb_id, json):

	image_url =''
	for item in json['included']:
		if item['id'] == thumb_id:
			image_url = item['attributes']['path']
			break

	image = BASE_URL + image_url

	return image
