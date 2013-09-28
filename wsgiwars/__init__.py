from pyramid.config import Configurator
from pyramid_beaker import session_factory_from_settings
from pyramid_beaker import set_cache_regions_from_settings

from pyramid.threadlocal import get_current_registry

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

    config.add_route('signup', '/signup')
    config.add_route('submitSignup', '/signup/submit')

    config.add_route('login', '/login')
    config.add_route('submitLogin', '/login/submit')

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
