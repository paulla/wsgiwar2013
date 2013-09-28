from pyramid.view import view_config



@view_config(route_name='home', renderer='templates/home.pt')
def home(request):
    return {'project': 'wsgiwars'}

@view_config(route_name='signup', renderer='templates/signup.pt')
def signup(request):
    return {}


@view_config(route_name='submitSignup', renderer='templates/submitSignup.pt')
def submitSignup(request):

    # TODO check is username isn't taken
    if request.matchdict['password'] == request.matchdict['confirmPassword']:
        # register user
        # Mika64 : your job !
        pass
    else:
        # redo :/
        pass
    return {}


