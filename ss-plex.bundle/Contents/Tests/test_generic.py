import plex_nose
from nose.tools import *
from helpers import listings_elements
import bridge

def setup_mocks():
    plex_nose.core.sandbox.publish_api(listings_elements.mocks, name = 'mocks')

class TestRenderListings(plex_nose.TestCase):
    def test_can_recover_from_errors():
        import mock
        @mock.patch.object(JSON, 'ObjectFromURL', return_value = Exception)
        def test(mock_json):
            container = generic.render_listings('/')
            rendered  = container.objects[0]

            eq_(len(container),  1)
            eqL_(rendered.title, 'heading.error')

        test()

class TestFlagTitle(plex_nose.TestCase):
    @classmethod
    def setup_class(cls):
        class stub(): pass

        persisted = dict(endpoint = '/foo', title = 'foo')
        favorite = dict(endpoint = '/shows/1', title = 'foo')
        favorite_collection = dict()
        favorite_collection[favorite['endpoint']] = favorite

        to_publish = stub()
        to_publish.persisted = persisted
        to_publish.favorite  = favorite
        to_publish.favorite_collection = favorite_collection

        plex_nose.core.sandbox.publish_api(to_publish, name = 'mocks')

    @classmethod
    def teardown_class(cls):
        plex_nose.core.sandbox.execute('del mocks')

    def test_default_flags():
        import mock

        @mock.patch.object(bridge.favorite, 'collection', return_value = mocks.favorite_collection)
        @mock.patch.object(bridge.download, 'queue', return_value = [mocks.persisted])
        def test(*a):
            default_favorite = generic.flag_title(mocks.favorite['title'],
                    mocks.favorite['endpoint'])
            default_persisted = generic.flag_title(mocks.persisted['title'],
                    mocks.persisted['endpoint'])
            default_nomatch = generic.flag_title('unknown', '/')

            eqF_(default_favorite, 'generic.flag-favorite')
            eqF_(default_persisted, 'generic.flag-persisted')
            eq_(default_nomatch, 'unknown')

            fpersisted_favorite = generic.flag_title(mocks.favorite['title'],
                    mocks.favorite['endpoint'], flags = ['persisted'])
            fpersisted_persisted = generic.flag_title(mocks.persisted['title'],
                    mocks.persisted['endpoint'], flags = ['persisted'])
            fpersisted_nomatch = generic.flag_title('unknown', '/',
                    flags = ['persisted'])

            eq_(fpersisted_favorite, mocks.favorite['title'])
            eqF_(fpersisted_persisted, 'generic.flag-persisted')
            eq_(fpersisted_nomatch, 'unknown')

            ffavorite_favorite = generic.flag_title(mocks.favorite['title'],
                    mocks.favorite['endpoint'], flags = ['favorite'])
            ffavorite_persisted = generic.flag_title(mocks.persisted['title'],
                    mocks.persisted['endpoint'], flags = ['favorite'])
            ffavorite_nomatch = generic.flag_title('unknown', '/',
                    flags = ['favorite'])

            eqF_(ffavorite_favorite, 'generic.flag-favorite')
            eq_(ffavorite_persisted, mocks.persisted['title'])
            eq_(ffavorite_nomatch, 'unknown')

        test()

class TestRenderListingsResponse(plex_nose.TestCase):
    @classmethod
    def setup_class(cls):
        setup_mocks()

    def test_can_render_endpoint():
        mocked    = mocks['endpoint']
        response  = dict(items = [ mocked ])
        container = generic.render_listings_response(response, '/')
        rendered  = container.objects[0]

        eq_('DirectoryObject', rendered.__class__.__name__)
        eq_(rendered.title,  mocked['display_title'])
        eqcb_(rendered.key,  generic.RenderListings,
                endpoint      = mocked['endpoint'],
                default_title = mocked['display_title']
                )

    def test_can_render_show():
        mocked    = mocks['show']
        response  = dict(items = [ mocked ])
        container = generic.render_listings_response(response, '/')
        rendered  = container.objects[0]

        eq_('TVShowObject',    rendered.__class__.__name__)
        eq_(rendered.title,    mocked['display_title'])
        eq_(rendered.summary,  mocked['display_overview'])
        eq_(rendered.thumb,    mocked['artwork'])
        eqcb_(rendered.key,    generic.ListTVShow,
                endpoint   = mocked['endpoint'],
                show_title = mocked['display_title'],
                refresh    = 0
                )

    def test_can_render_episode():
        mocked    = mocks['episode']
        response  = dict(items = [ mocked ])
        container = generic.render_listings_response(response, '/')
        rendered  = container.objects[0]

        eq_('PopupDirectoryObject',  rendered.__class__.__name__)
        eq_(rendered.title,    mocked['display_title'])
        eq_(rendered.summary,  mocked['display_overview'])
        eq_(rendered.thumb,    mocked['artwork'])
        eqcb_(rendered.key,    generic.WatchOptions,
                endpoint   = mocked['endpoint'],
                title      = mocked['display_title'],
                media_hint = 'show'
                )

    def test_can_render_movie():
        mocked    = mocks['movie']
        response  = dict(items = [ mocked ])
        container = generic.render_listings_response(response, '/')
        rendered  = container.objects[0]

        eq_('PopupDirectoryObject',  rendered.__class__.__name__)
        eq_(rendered.title,    mocked['display_title'])
        eq_(rendered.summary,  mocked['display_overview'])
        eq_(rendered.thumb,    mocked['artwork'])
        eqcb_(rendered.key,    generic.WatchOptions,
                endpoint   = mocked['endpoint'],
                title      = mocked['display_title'],
                media_hint = 'movie'
                )

    def test_can_render_foreign():
        from ss.util import q

        mocked    = mocks['foreign']
        response  = dict(items = [ mocked, mocked ])
        container = generic.render_listings_response(response, '/')
        first     = container.objects[0]
        second    = container.objects[1]

        eq_('VideoClipObject', first.__class__.__name__)
        eq_(first.title, mocked['domain'])
        eq_(first.url, generic.wizard_url('/', 0))

        eq_('VideoClipObject', second.__class__.__name__)
        eq_(second.title, mocked['domain'])
        eq_(second.url, generic.wizard_url('/', 1))

    def test_can_suggest_title():
        response  = dict()
        suggested = 'foo'
        container = generic.render_listings_response(response, '/',
                default_title = suggested)

        eqL_(container.title1, 'foo')

    def test_cannot_suggest_title_when_exists():
        response  = dict(title = 'bar')
        suggested = 'foo'
        container = generic.render_listings_response(response, '/',
                default_title = suggested)

        eqL_(container.title1, 'bar')

class TestIcons(plex_nose.TestCase):
    def test_icon_for_tv():
        mocked    = dict(endpoint = '/shows', _type = 'endpoint')
        response  = dict(items = [ mocked ])
        container = generic.render_listings_response(response, '/')
        rendered  = container.objects[0]

        ok_('icon-tv.png' in rendered.thumb)

    def test_icon_for_movies():
        mocked    = dict(endpoint = '/movies', _type = 'endpoint')
        response  = dict(items = [ mocked ])
        container = generic.render_listings_response(response, '/')
        rendered  = container.objects[0]

        ok_('icon-movies.png' in rendered.thumb)

class TestWatchOptions(plex_nose.TestCase):
    @classmethod
    def setup_class(cls):
        setup_mocks()

    def test_when_fresh():
        generic.JSON.ObjectFromURL = lambda *a, **k: dict()

        container = generic.WatchOptions(endpoint = '/', title = 'foo', media_hint = 'show')
        watch_now_key = generic.wizard_url('/')

        ok_(container.no_cache)
        eq_(len(container), 3)

        eq_('VideoClipObject', container.objects[0].__class__.__name__)
        # May be due to the fact that it is a VideoClipObject
        # but we cannot test against I18N key here
        eq_(container.objects[0].title,   'Watch Now')
        eq_(container.objects[0].url,     watch_now_key)

        eqL_(container.objects[1].title,  'media.watch-later')
        eqL_(container.objects[2].title,  'media.all-sources')

    def test_when_in_history():
        import mock

        @mock.patch.object(JSON, 'ObjectFromURL')
        @mock.patch.object(bridge.download, 'includes', return_value = True)
        def test(*a):
            container = generic.WatchOptions(endpoint = '/', title = 'foo', media_hint = 'show')
            eqL_(container.objects[1].title, 'media.persisted')

        test()

    def test_when_in_queue():
        import mock

        @mock.patch.object(JSON, 'ObjectFromURL')
        @mock.patch.object(bridge.download, 'queue', return_value = [dict(endpoint = '/')])
        def test(*a):
            container = generic.WatchOptions(endpoint = '/', title = 'foo', media_hint = 'show')
            eqL_(container.objects[1].title, 'media.persisted')

        test()

    def test_when_is_downloading():
        import mock

        @mock.patch.object(JSON, 'ObjectFromURL')
        @mock.patch.object(bridge.download, 'current', return_value = dict(endpoint = '/'))
        @mock.patch.object(bridge.download, 'assumed_running', return_value = True)
        def test(*a):
            container = generic.WatchOptions(endpoint = '/', title = 'foo', media_hint = 'show')
            eqL_(container.objects[1].title, 'media.persisted')

        test()

    def test_with_suggestions():
        import mock

        @mock.patch.object(JSON, 'ObjectFromURL', return_value = dict(items = [ mocks['show'] ]))
        def test(mock_json):
            container = generic.WatchOptions(endpoint = '/', title = 'foo', media_hint = 'show')

            eq_(4, len(container))
            eq_(container.objects[3].title, mocks['show']['display_title'])

        test()

class TestListTvShow(plex_nose.TestCase):
    @classmethod
    def setup_class(cls):
        setup_mocks()

    def setUp(self):
        bridge.favorite.append(endpoint = '/shows/1', title = 'foo')

    def tearDown(self):
        bridge.favorite.clear()

    def test_removes_show_title():
        import mock
        import plex_nose

        def download_includes(e):
            if mocks['episode2']['endpoint'] == e:
                return True

            return False

        response = dict(
            items = [ mocks['episode'], mocks['episode2'] ],
            resource = mocks['show']
        )
        @mock.patch.object(bridge.favorite, 'includes', return_value = True)
        @mock.patch.object(bridge.download, 'includes', side_effect = download_includes)
        @mock.patch.object(JSON, 'ObjectFromURL', return_value = response)
        def test(*a):
            container = generic.ListTVShow(endpoint = '/shows/1', show_title = 'foo')
            first = container.objects[1]
            second = container.objects[2]

            eq_(first.title, '1x1 episode title')
            eq_(second.title, u'\u21E3 episode title 01.01.2013')

        test()
