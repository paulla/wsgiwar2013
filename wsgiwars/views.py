import datetime

from pyramid.view import view_config
from pyramid.threadlocal import get_current_registry
from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPNotFound
from pyramid.security import remember
from pyramid.security import forget

from pyramid_mailer.mailer import Mailer
from pyramid_mailer.message import Message

import bcrypt

import couchdbkit
from couchdbkit.designer import push

from wsgiwars.models.user import User
from wsgiwars.models.link import Link

settings = get_current_registry().settings

server = couchdbkit.Server(settings['couchdb.url'])
db = server.get_or_create_db(settings['couchdb.db'])

User.set_db(db)
Link.set_db(db)

push('couchdb/_design/user', db)
push('couchdb/_design/public', db)
push('couchdb/_design/user_link', db)

@view_config(route_name='home', renderer='templates/home.pt')
def home(request):
    links = Link.view('public/all',  limit=10, descending=True)

    return {'project': 'wsgiwars',
            'links': links}

@view_config(route_name='delete_user')
def delete(request):
    #TODO if login
    #TODO check is admin
    user = User.get(request.matchdict['user'])
    user.delete()
    return HTTPFound(location=request.route_url('admin_list',page="0"))

@view_config(route_name='admin')
def admin(request):
    return HTTPFound(location=request.route_url('admin_list',page="0"))

@view_config(route_name='admin_list', renderer='templates/admin.pt')
def admin_list(request):
    #TODO if login
    #TODO check is admin
    skip = int(request.matchdict['page'])*10
    users = User.view('user/all', skip = skip , limit = 10, descending=True)
    return {'users': users}

@view_config(route_name='admin_user', renderer='templates/admin_user.pt')
def admin_user(request):
    #TODO if login
    #TODO check is admin
    user = User.get(request.matchdict['user'])
    if request.method == 'POST':
        user.name = request.POST.get('name')
        user.description = request.POST.get('description')
        user.save()
    return {'user' : user}

@view_config(route_name='about', renderer='templates/about.pt')
def about(request):
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

    if not request.POST['password'].strip():
        request.session.flash(flashError)
        return HTTPFound(location=request.route_path('login'))

    try:
        user = User.get(request.POST['login'])
    except couchdbkit.exceptions.ResourceNotFound:
        request.session.flash(flashError)
        return HTTPFound(location=request.route_path('login'))

    if bcrypt.hashpw(request.POST['password'].encode('utf-8'), user.password) != user.password:
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

    try:
        User.get(request.POST['login'])
    except couchdbkit.exceptions.ResourceNotFound:
        pass
    else:
        request.session.flash(u"Username already exist")
        return HTTPFound(location=request.route_path('signup'))

    if not request.POST['password'].strip():
        request.session.flash(u"You realy need a password")
        return HTTPFound(location=request.route_path('signup'))

    if request.POST['password'] == request.POST['confirmPassword']:
        password = bcrypt.hashpw(request.POST['password'].encode('utf-8'), bcrypt.gensalt())

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
    return {'link': None}

@view_config(route_name='copyLink', renderer='templates/addlink.pt')
def copylink(request):
    link = Link.get(request.matchdict['link'])

    if link.private:
        raise HTTPNotFound()

    return {'link': link}

@view_config(route_name='submitLink')
def submitlink(request):

    #TODO check logged
    #TODO check if not already submit by user

    tags = [tag for tag in request.POST['tags'].split(',')]

    link = Link()
    link.url = request.POST['link']
    link.created = datetime.datetime.now()
    link.comment = request.POST['comment'].strip()
    link.userID = request.session['login']
    link.username = request.session['username']
    link.private = False  # TODO
    link.tags = tags

    if 'private' in request.POST:
        link.private = True

    link.save()

    request.session.flash("link added !")
    return HTTPFound(location=request.route_path('home'))

@view_config(route_name="user", renderer="templates/user.pt")
def user(request):
    """
    """
    try:
        user = User.get(request.matchdict['userid'])
    except couchdbkit.exceptions.ResourceNotFound:
        return HTTPNotFound()


    links = Link.view('user_link/all',  limit=10, descending=True, key=user._id)

    return {'links': links, 'user': user}

