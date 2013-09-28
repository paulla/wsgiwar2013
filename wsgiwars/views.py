from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from pyramid_mailer.mailer import Mailer
from pyramid_mailer.message import Message


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

        mailer = Mailer()
        message = Message(subject="Your subsription !",
                          sender=request.registry.settings['mail_from'],
                          recipients=[request.POST['email']],
                          body="Confirm the link") # TODO add link


        mailer.send(message)

        return {'name': request.POST['name']}

    else:

        return HTTPFound(location=request.route_path('signup'))



