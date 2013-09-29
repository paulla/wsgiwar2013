import datetime
import tempfile
import os

from pyramid.view import view_config
from pyramid.threadlocal import get_current_registry
from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPNotFound
from pyramid.security import remember
from pyramid.response import Response

from pyramid_mailer.mailer import Mailer
from pyramid_mailer.message import Message

import bcrypt

import couchdbkit
from couchdbkit.designer import push

from PIL import Image

from wsgiwars.models.user import User
from wsgiwars.models.link import Link

settings = get_current_registry().settings

server = couchdbkit.Server(settings['couchdb.url'])
db = server.get_or_create_db(settings['couchdb.db'])

User.set_db(db)
Link.set_db(db)

for view in ['couchdb/_design/user',
             'couchdb/_design/public',
             'couchdb/_design/user_link',
             'couchdb/_design/my_link',
             'couchdb/_design/viewTag',
             'couchdb/_design/viewFollowers', ]:
    push(view, db)

avatarSize = 128,128

def limitAndPage(request):
    # TODO validators ?
    limit = 10
    page = 0

    if 'limit' in request.GET:
        try:
            limit = int(request.GET['limit'])
        except ValueError:
            pass

    if 'page' in request.GET:
        try:
            page = int(request.GET['page'])
            if page < 0:
                page = 0
        except ValueError:
            pass

    return limit, page
@view_config(route_name='home', renderer='templates/home.pt')
def home(request):

    limit, page = limitAndPage(request)

    links = Link.view('public/all',  limit=limit, descending=True, skip=limit*page)

    return {'links': links, 'page': page, 'limit':limit}


@view_config(route_name='delete_user', logged=True, is_admin=True)
def delete(request):
    user = User.get(request.matchdict['user'])
    user.delete()
    return HTTPFound(location=request.route_url('admin_list', page="0"))


@view_config(route_name='admin', logged=True,  is_admin=True)
def admin(request):
    return HTTPFound(location=request.route_url('admin_list', page="0"))


@view_config(route_name='admin_list', renderer='templates/admin.pt', logged=True, is_admin=True)
def admin_list(request):
    limit, page = limitAndPage(request)

    skip = limit*page
    users = User.view('user/all', skip=skip, limit=limit, descending=True)

    return {'users': users,
            'page': page}


@view_config(route_name='admin_user', renderer='templates/admin_user.pt', logged=True, is_admin=True)
def admin_user(request):
    user = User.get(request.matchdict['user'])
    # TODO @cyp to @Mika64 need to restrain view_config to POST ?
    if request.method == 'POST':
        user.name = request.POST.get('name')
        user.description = request.POST.get('description')
        if request.POST.get('admin') == 'on':
            user.is_admin = True
        else:
            user.is_admin = False
        user.save()
    return {'user': user}


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

    if bcrypt.hashpw(request.POST['password'].encode('utf-8'),
                     user.password) != user.password:
        request.session.flash(flashError)

        return HTTPFound(location=request.route_path('login'))

    request.session.flash(u"welcome %s, you are logged" % user.name)

    headers = remember(request, user._id)
    request.session['username'] = user.name
    request.session['login'] = user._id
    request.session['is_admin'] = user.is_admin
    request.session.save()

    return HTTPFound(location=request.route_path('home'), headers=headers)


@view_config(route_name='submitSignup',
             renderer='templates/signupSubmit.pt')
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
        password = bcrypt.hashpw(request.POST['password'].encode('utf-8'),
                                 bcrypt.gensalt())

        user = User(password=password,
                    name=request.POST['name'],
                    description=request.POST['description'],
                    mail=request.POST['email'],
                    )
        user._id = request.POST['login']
        user.save()

        if hasattr(request.POST['avatar'], 'filename'):
            tmph, originImage = tempfile.mkstemp(dir=settings['tmp'], suffix="original")
            os.close(tmph)

            tmph, thumbImage = tempfile.mkstemp(dir=settings['tmp'], suffix="thumb")
            os.close(tmph)

            with open(originImage, 'wb') as tmp:
                tmp.write(request.POST['avatar'].file.read())

            fullSize = Image.open(originImage)
            fullSize.thumbnail(avatarSize, Image.ANTIALIAS)
            fullSize.save(thumbImage , "JPEG")

            with open(thumbImage, 'rb') as thumb:
                user.put_attachment(thumb, 'avatar')

            os.remove(originImage)
            os.remove(thumbImage)

        mailer = Mailer()
        message = Message(subject="Your subsription !",
                          sender=settings['mail_from'],
                          recipients=[request.POST['email']],
                          body="Confirm the link")  # TODO add link

        mailer.send(message)

        return {'name': request.POST['name']}

    else:

        return HTTPFound(location=request.route_path('signup'))


@view_config(route_name='addLink', renderer='templates/addlink.pt', logged=True)
def addlink(request):
    return {'link': None}


@view_config(route_name='copyLink', renderer='templates/addlink.pt', logged=True)
def copylink(request):
    link = Link.get(request.matchdict['link'])

    if link.private:
        raise HTTPNotFound()

    return {'link': link}


@view_config(route_name='submitLink', logged=True)
def submitlink(request):

    # TODO check if not already submit by user

    tags = [tag.strip() for tag in request.POST['tags'].split(',')]

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

    limit, page = limitAndPage(request)

    links = Link.view('user_link/all',  limit=limit,
                      skip=limit*page, descending=True,
                      startkey=[user._id, {}], endkey=[user._id],
                      include_docs=True)

    return {'links': links, 'user': user, 'limit':limit, 'page': page}


@view_config(route_name="mylinks", renderer="templates/mylinks.pt", logged=True)
def mylinks(request):
    limit, page = limitAndPage(request)

    links = Link.view('my_link/all', limit=limit,
                      descending=True, skip=page*limit,
                      startkey=[request.session['login'], {}],
                      endkey=[request.session['login']], include_docs=True)

    return {'links': links}


@view_config(route_name="tag", renderer="templates/tag.pt")
def tag(request):
    limit, page = limitAndPage(request)

    links = Link.view('viewTag/all', limit=limit,
                      descending=True, skip=page*limit,
                      startkey=[request.matchdict['tag'], {}],
                      endkey=[request.matchdict['tag']])
    return {'links': links}


@view_config(route_name='logout', logged=True)
def logout(request):
    request.session.delete()
    return HTTPFound(location=request.route_path('home'))


@view_config(route_name='rss', renderer='templates/rss.pt')
def rss(request):
    links = Link.view('public/all',  limit=10, descending=True)
    return {'links': links}


@view_config(route_name="tagrss", renderer="templates/tagrss.pt")
def tagrss(request):
    links = Link.view('viewTag/all', limit=10, descending=True,
                      startkey=[request.matchdict['tag'], {}],
                      endkey=[request.matchdict['tag']])
    return {'links': links}


@view_config(route_name="userrss", renderer="templates/userrss.pt")
def userrss(request):
    """
    """
    try:
        user = User.get(request.matchdict['userid'])
    except couchdbkit.exceptions.ResourceNotFound:
        return HTTPNotFound()

    links = Link.view(
        'user_link/all',  limit=10, descending=True, key=user._id)

    return {'links': links, 'user': user}


@view_config(route_name='link', renderer='templates/link.pt')
def link(request):
    link = Link.get(request.matchdict['link'])

    if link.private:
        raise HTTPNotFound()

    return {'link': link}


@view_config(route_name='contacts', renderer='templates/contacts.pt', logged=True)
def contacts(request):
    limit, page = limitAndPage(request)

    users = User.view('viewFollowers/all', limit=limit,
                      descending=True, skip=limit*page,
                      key=request.session['login'])

    return {"users": users}


@view_config(route_name='submitContact', renderer='templates/submit_contact.pt', logged=True)
def submitContact(request):
    if not(request.POST['contactid'].strip()):
        request.session.flash("contact id is required")
        HTTPFound(location=request.route_path('contacts'))

    try:
        user = User.get(request.POST['contactid'].strip())
    except couchdbkit.exceptions.ResourceNotFound:
        request.session.flash("Sorry, we don't find your buddy.")
        return HTTPFound(location=request.route_path('contacts'))

    if request.session['login'] in user.followers:
        request.session.flash("You already follow %s." % user.name)
        return HTTPFound(location=request.route_path('contacts'))

    user.followers.append(request.session['login'])
    user.save()

    request.session.flash("You follow %s." % user.name)
    return HTTPFound(location=request.route_path('contacts'))


@view_config(route_name="unfollow", renderer='templates/unfollow.pt', logged=True)
def unfollow(request):
    try:
        user = User.get(request.matchdict['userid'].strip())
    except couchdbkit.exceptions.ResourceNotFound:
        request.session.flash("Sorry, we don't find your buddy.")
        return HTTPFound(location=request.route_path('contacts'))

    return {"user": user}


@view_config(route_name="confirmUnfollow", logged=True)
def confirmUnfollow(request):
    try:
        user = User.get(request.matchdict['userid'].strip())
    except couchdbkit.exceptions.ResourceNotFound:
        request.session.flash("Sorry, we don't find your buddy.")
        return HTTPFound(location=request.route_path('contacts'))

    user.followers = [follower for follower in user.followers
                      if follower != request.session['login']]

    user.save()

    request.session.flash("You don't follower %s anymore" % user.name)
    return HTTPFound(location=request.route_path('contacts'))

@view_config(route_name="profile", renderer='templates/profile.pt', logged=True)
def profile(request):
    user = User.get(request.session['login'])

    if request.method =='POST':

        flashError = "Sorry dude : wrong password"

        if not request.POST['initPassword'].strip():
            request.session.flash('No password provided')
            return {'user':user}

        elif not bcrypt.hashpw(request.POST['initPassword'].encode('utf-8'), user.password) == user.password:
            request.session.flash(flashError)
            return {'user':user}

        if request.POST['submitDelete']:
            request.session.delete()
            user.delete()
            mailer = Mailer()
            message = Message(subject="Account deleted", \
                             sender=settings['mail_from'], \
                             recipients=user.mail, \
                             body="Your account have been deleted")
            mailer.send(message)
            return HTTPFound(location=request.route_path('home'))

        if request.POST['newPassword'].strip():
            if request.POST['newPassword'] == request.POST['confirmPassword']:
                password = bcrypt.hashpw(request.POST['newPassword'].encode('utf-8'), bcrypt.gensalt())
                user.password = password
            else:
                request.session.flash(u"Password not confirm")
                return {'user' : user}

        user.name = request.POST['name']
        user.description = request.POST['description']
        user.mail = request.POST['email']
        user.save()
        request.session.flash(u"Modification saved !")

    return {'user':user}

@view_config(route_name='avatar')
def avatar(request):
    try:
        user = User.get(request.matchdict['userid'].strip())
    except couchdbkit.exceptions.ResourceNotFound:
        raise HTTPNotFound()

    response = Response(content_type='image/jpeg',
                        body=user.fetch_attachment('avatar'))

    return response
