from pyramid.config import Configurator
from pyramid_beaker import session_factory_from_settings
from pyramid_beaker import set_cache_regions_from_settings

from pyramid.threadlocal import get_current_registry

from wsgiwars.predicate import LoggedPredicate

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """

    sessionFactory = session_factory_from_settings(settings)
    set_cache_regions_from_settings(settings)

    config = Configurator(settings=settings)
    config.set_session_factory(sessionFactory)

    get_current_registry().settings = settings

    config.add_static_view('static', 'static', cache_max_age=3600)

    config.add_route('home', '/')
    config.add_route('about', '/about')
    config.add_route('admin', '/admin')
    config.add_route('admin_list', '/admin/{page}')
    config.add_route('admin_user', '/admin/detail/{user}')
    config.add_route('delete_user', '/admin/delete/user/{user}')

    config.add_route('signup', '/signup')
    config.add_route('submitSignup', '/signup/submit')

    config.add_route('logout', '/logout')
    config.add_route('login', '/login')
    config.add_route('submitLogin', '/login/submit')

    config.add_route('addLink', '/link/add')
    config.add_route('submitLink', '/link/submit')

    config.add_route("copyLink", '/copy/{link}')
    config.add_route("link", '/link/{link}')

    config.add_route("mylinks", '/mylinks')
    config.add_route('user', '/user/{userid}')
    config.add_route('changePassword', '/changePassword')
    config.add_route('submitChangePassword', '/changePassword/submit')

    config.add_route('tag', '/tag/{tag}')

    config.add_route('rss', '/rss')
    config.add_route('userrss', '/user/{userid}/rss')
    config.add_route('tagrss', '/tag/{tag}/rss')

    config.add_view_predicate('logged', LoggedPredicate)

    for include in ['pyramid_mailer',
                    'pyramid_fanstatic',
                    'pyramid_chameleon',
                    'pyramid_beaker',
                    'rebecca.fanstatic',]:

        config.include(include)

    config.add_fanstatic_resources(['js.bootstrap.bootstrap',
                                    'js.bootstrap.bootstrap',
                                    'css.fontawesome.fontawesome',
                                    ]
                                   , r'.*\.pt')

    config.scan()
    return config.make_wsgi_app()
