FEATURE_PREFIX = '%s/search' % consts.prefix
from generic import render_listings
import re

@route(FEATURE_PREFIX)
def MainMenu():
    container = container_for('heading.search')

    for query in ss.util.sorted_by_title(bridge.search.collection()):
        container.add(button(query, SearchResultsMenu, query = query, foo = 1))

    return container

def ResultsMenu(query, foo = 1):

    if 'Roku' == Client.Platform and (re.search('\s*\(\d*\)', query)):
        query = re.sub('\s*\(\d*\)\s*','',query)

    container = render_listings('/search/%s' % ss.util.q(query))
    labels    = [ 'add', 'remove' ]
    response  = int(bridge.search.includes(query))

    container.objects.insert(0, button('search.heading.%s' % labels[response], Toggle, query = query))
    return container

@route('%s/toggle' % FEATURE_PREFIX)
def Toggle(query):
    message = 'search.response.%s' % bridge.search.toggle(query)
    return dialog('heading.search', message)
