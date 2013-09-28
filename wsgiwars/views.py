from pyramid.view import view_config
from pyramid.threadlocal import get_current_registry
from pyramid.httpexceptions import HTTPFound
from pyramid.security import remember
from pyramid.security import forget

from pyramid_mailer.mailer import Mailer
from pyramid_mailer.message import Message

import bcrypt

import couchdbkit

from wsgiwars.models.user import User

settings = get_current_registry().settings

server = couchdbkit.Server(settings['couchdb.url'])
db = server.get_or_create_db(settings['couchdb.db'])
User.set_db(db)


@view_config(route_name='home', renderer='templates/home.pt')
def home(request):
    return {'project': 'wsgiwars'}

@view_config(route_name='signup', renderer='templates/signup.pt')
def signup(request):
    return {}

@view_config(route_name='login', renderer='templates/login.pt')
def login(request):
    return {}

@view_config(route_name='submitLogin')
def submitLogin(request):

    flashError = "Sorry dude : wrong login or password"

    try:
        user = User.get(request.POST['login'])
    except couchdbkit.exceptions.ResourceNotFound:
        request.session.flash(flashError)
        return HTTPFound(location=request.route_path('login'))

    if bcrypt.hashpw(request.POST['password'], user.password) != user.password:
        request.session.flash(flashError)

        return HTTPFound(location=request.route_path('login'))

    request.session.flash(u"welcome %s, you are logged" % user.name)

    headers = remember(request, user._id)
    request.session['username'] = user.name
    request.session['login'] = user._id
    request.session.save()

    return HTTPFound(location=request.route_path('home'), headers=headers)


@view_config(route_name='submitSignup', renderer='templates/signupSubmit.pt')
def submitSignup(request):
    # TODO check is username isn't taken

    if request.POST['password'] == request.POST['confirmPassword']:
        password = bcrypt.hashpw(request.POST['password'], bcrypt.gensalt())

        user = User(password=password,
                    avatar=request.POST['avatar'],
                    name=request.POST['name'],
                    description=request.POST['description'],
                    )
        user._id = request.POST['login']
        user.save()

        mailer = Mailer()
        message = Message(subject="Your subsription !",
                          sender=settings['mail_from'],
                          recipients=[request.POST['email']],
                          body="Confirm the link") # TODO add link


        mailer.send(message)

        return {'name': request.POST['name']}

    else:

        return HTTPFound(location=request.route_path('signup'))

@view_config(route_name='addLink', renderer='templates/addlink.pt')
def addlink(request):
    return {}
