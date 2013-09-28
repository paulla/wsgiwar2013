from pyramid.view import view_config
from pyramid.threadlocal import get_current_registry
from pyramid.httpexceptions import HTTPFound

from pyramid_mailer.mailer import Mailer
from pyramid_mailer.message import Message

import bcrypt

import couchdbkit

from paulla.wsgiwar2013.models.users import User

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


@view_config(route_name='submitSignup', renderer='templates/signupSubmit.pt')
def submitSignup(request):

    # TODO check is username isn't taken
    if request.POST['password'] == request.POST['confirmPassword']:
        # register user
        # Mika64 : your job !
        password = bcrypt.hashpw(request.POST['password'], bcrypt.gensalt())

        user = User(password=password,
                    avatar=request.POST['avatar'],
                    name=request.POST['name'],
                    description=request.POST['description'],
                    )
        user._id = request.POST['username']
        user.save()

        mailer = Mailer()
        message = Message(subject="Your subsription !",
                          sender=request.registry.settings['mail_from'],
                          recipients=[request.POST['email']],
                          body="Confirm the link") # TODO add link


        mailer.send(message)

        return {'name': request.POST['name']}

    else:

        return HTTPFound(location=request.route_path('signup'))



