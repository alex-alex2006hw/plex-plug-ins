NAME = 'South Park'
ART = 'art-default.jpg'
ICON = 'icon-default.jpg'
BASE_URL = 'http://southpark.cc.com'
GUIDE_URL = '%s/full-episodes' % (BASE_URL)

RE_SEASON_EPISODE = Regex('full-episodes\/s([0-9]+)e([0-9]+)')

####################################################################################################
def Start():

	ObjectContainer.title1 = NAME
	HTTP.CacheTime = CACHE_1HOUR
	HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.94 Safari/537.36'

###################################################################################################
@handler('/video/southpark', NAME, art=ART, thumb=ICON)
def MainMenu():

	oc = ObjectContainer()
	num_seasons = HTML.ElementFromURL(GUIDE_URL).xpath('//*[contains(@data-value, "season-")]/@data-value')[-1].split('-')[-1]

	for season in reversed(range(1, int(num_seasons)+1)):

		title = 'Season %s' % (str(season))
		oc.add(
			DirectoryObject(
				key = Callback(Episodes, title=title, season=str(season)),
				title = title
			)
		)

	return oc

####################################################################################################
@route('/video/southpark/episodes')
def Episodes(title, season):

	oc = ObjectContainer(title2=title)
	html = HTML.ElementFromURL('%s/season-%s?sort=!airdate' % (GUIDE_URL, season))

	json_url = html.xpath('//section[@data-url]/@data-url')[0]
	json_url = json_url.replace('{resultsPerPage}', '30')
	json_url = json_url.replace('{currentPage}', '1')
	json_url = json_url.replace('{sort}', '!airdate')
	json_url = json_url.replace('{relatedItemId}', 'season-%s' % (season))

	json_obj = JSON.ObjectFromURL('%s%s' % (BASE_URL, json_url))

	for episode in json_obj['results']:

		if episode['_availability'] == 'beforepremiere':
			continue

		url = episode['_url']['default'].split('#')[0]

		try:
			index = int(RE_SEASON_EPISODE.search(url).group(2))
		except:
			continue

		title = episode['title']
		summary = episode['description']

		if title == 'TBD' or summary.startswith('This episode airs '):
			continue

		thumb = episode['images']

		oc.add(
			EpisodeObject(
				url = url,
				show = NAME,
				title = '%sx%d %s' % (season, index, title),
				summary = summary,
				index = index,
				season = int(season),
				thumb = Resource.ContentsOfURLWithFallback(thumb)
			)
		)

	if len(oc) < 1:
		return ObjectContainer(header="Empty", message="This season doesn't contain any episodes.")
	else:
		oc.objects.sort(key = lambda obj: obj.index)
		return oc
