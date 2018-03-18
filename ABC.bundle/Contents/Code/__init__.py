import ssl, urllib2

NAME = 'ABC'
ART = 'art-default.jpg'
ICON = 'icon-default.jpg'

ALL_SHOWS = 'https://api.pluto.watchabc.go.com/api/ws/pluto/v1/module/tilegroup/1389461?brand=001&device=002&start=0&size=200'
SHOW_SEASONS = 'https://api.pluto.watchabc.go.com/api/ws/pluto/v1/layout?brand=001&device=002&type=show&show=%s'
SHOW_EPISODES = 'https://api.pluto.watchabc.go.com/api/ws/pluto/v1/module/tilegroup/1925878?brand=001&device=002&show=%s&season=%s&start=0&size=50'

HTTP_HEADERS = {
	'User-Agent': 'ABC/5.0.14(iPad4,4; cpu iOS 10_2_1 like mac os x; en_nl) CFNetwork/758.5.3 Darwin/15.6.0',
	'appversion': '5.0.14'
}

RE_SECTION_TITLE = Regex('^season (\d+)$', Regex.IGNORECASE)

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
	HTTP.ClearCache()

####################################################################################################
@handler('/video/abc', NAME, art=ART, thumb=ICON)
def MainMenu():

	oc = ObjectContainer()
	json_obj = JSON.ObjectFromString(GetData(ALL_SHOWS))

	for show in json_obj['tiles']:

		if not 'show' in show:
			continue

		if not 'id' in show['show'] or show['show']['id'] in ['', None]:
			continue

		id = show['show']['id']
		title = show['title']
		thumb = show['images'][0]['value'] if 'images' in show else ''

		oc.add(DirectoryObject(
			key = Callback(Season, title=title, id=id),
			title = title,
			thumb = thumb
		))

	return oc

####################################################################################################
@route('/video/abc/season')
def Season(title, id):

	oc = ObjectContainer(title2=title)
	json_obj = JSON.ObjectFromString(GetData(SHOW_SEASONS % (id)))

	for section in json_obj['modules']:

		if 'title' not in section:
			continue

		season = RE_SECTION_TITLE.search(section['title'])

		if season:

			oc.add(DirectoryObject(
				key = Callback(Episodes, title=title, id=id, season=season.group(1)),
				title = 'Season %s' % (season.group(1))
			))

	if len(oc) < 1:
		oc.header = "No episodes available"
		oc.message = "There aren't any episodes available for this show"

	return oc

####################################################################################################
@route('/video/abc/episodes')
def Episodes(title, id, season):

	oc = ObjectContainer(title2=title)
	json_obj = JSON.ObjectFromString(GetData(SHOW_EPISODES % (id, season)))

	for episode in json_obj['tiles']:

		if 'accesslevel' in episode['video'] and episode['video']['accesslevel'] != "0":
			continue

		oc.add(EpisodeObject(
			url = 'abc://%s' % (episode['video']['id']),
			show = episode['video']['show']['title'],
			title = episode['video']['title'],
			summary = episode['video']['longdescription'],
			duration = episode['video']['duration'],
			content_rating = episode['video']['tvrating'],
			originally_available_at = Datetime.ParseDate(episode['video']['airtime']).date(),
			season = int(episode['video']['seasonnumber']),
			index = int(episode['video']['episodenumber']),
			thumb = episode['images'][0]['value']
		))

	if len(oc) < 1:
		oc.header = "No episodes available"
		oc.message = "There aren't any episodes available for this season"

	return oc

####################################################################################################
@route('/video/abc/getdata')
def GetData(url):

	# Quick and dirty workaround
	# Do not validate ssl certificate
	# http://stackoverflow.com/questions/27835619/ssl-certificate-verify-failed-error
	req = urllib2.Request(url, headers=HTTP_HEADERS)
	ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
	data = urllib2.urlopen(req, context=ssl_context).read()

	return data
