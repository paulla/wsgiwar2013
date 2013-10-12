############################################################################
# The MIT License (MIT)
#
# Copyright (c) 2013 PauLLA
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNES FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
############################################################################

""" PauLLA WSGI Wrestle 2013 Delicious like
"""

from pyramid.config import Configurator
from pyramid_beaker import session_factory_from_settings
from pyramid_beaker import set_cache_regions_from_settings

from pyramid.threadlocal import get_current_registry

from wsgiwars.predicate import LoggedPredicate, Is_AdminPredicate


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
    config.add_route('admin_list', '/admin/users/{page}')
    config.add_route('admin_user', '/admin/detail/{user}')
    config.add_route('delete_user', '/admin/delete/user/{user}')

    config.add_route('signup', '/signup')
    config.add_route('submitSignup', '/signup/submit')

    config.add_route('logout', '/logout')
    config.add_route('login', '/login')
    config.add_route('submitLogin', '/login/submit')
    config.add_route('checkLogin', '/check/{userid}/{randomid}')
    config.add_route('submitcheckLogin', '/check/{userid}/{randomid}/submit')

    config.add_route('addLink', '/link/add')
    config.add_route('submitLink', '/link/submit')

    config.add_route("copyLink", '/copy/{link}')
    config.add_route("link", '/link/{link}')
    config.add_route('comment', '/comment/{link}')
    config.add_route('rmComment', '/rmcomment/{link}/{userid}/{date}')
    config.add_route("rmLink", '/link/delete/{link}')

    config.add_route("mylinks", '/mylinks')
    config.add_route('user', '/user/{userid}')
    config.add_route('profile', '/profile')

    config.add_route('avatar', '/avatar/{userid}')

    config.add_route('tag', '/tag/{tag}')

    config.add_route('rss', '/rss')
    config.add_route('userrss', '/user/{userid}/rss')
    config.add_route('tagrss', '/tag/{tag}/rss')

    config.add_route('contacts', '/contacts')
    config.add_route('submitContact', '/submitContact')
    config.add_route('unfollow', '/unfollow/{userid}')
    config.add_route('confirmUnfollow', '/confirmUnfollow/{userid}')
    config.add_route('contactsLinks', '/contactsLinks')

    config.add_route('cloudTags', '/cloudTags')

    config.add_route('getTitle', '/ajax/gettitle')

    config.add_view_predicate('logged', LoggedPredicate)
    config.add_view_predicate('is_admin', Is_AdminPredicate)

    for include in ['pyramid_mailer',
                    'pyramid_fanstatic',
                    'pyramid_chameleon',
                    'pyramid_beaker',
                    'rebecca.fanstatic', ]:

        config.include(include)

    config.add_fanstatic_resources(['js.bootstrap.bootstrap',
                                    'js.bootstrap.bootstrap_theme',
                                    'css.fontawesome.fontawesome',
                                    ], r'.*\.pt')

    config.scan()
    return config.make_wsgi_app()
