from pyramid.view import view_config

import bcrypt

import couchdbkit

from paulla.wsgiwar2013.models.users import Users_db


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

        user = Users_db(username = request.POST['username'],
                password = password,
                avatar = request.POST['avatar'],
                name = request.POST['name']
                description = request.POST['description']
                )

        user.save()

        from pyramid_mailer.mailer import Mailer
        from pyramid_mailer.message import Message

        mailer = Mailer()
        message = Message(subject="Your subsription !",
                          sender=request.registry.settings['mail_from'],
                          recipients=[request.POST['email']],
                          body="Confirm the link") # TODO add link


        mailer.send(message)

        return {}

    else:
        # redo :/
        pass
    return {}


