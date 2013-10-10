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

import datetime
import tempfile
import os
import random

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
             'couchdb/_design/viewFollowers',
             'couchdb/_design/contacts_links',
             'couchdb/_design/tags',
             ]:
    push(view, db)

avatarSize = 128,128

def limitAndPage(request):
    """
    Set the limit and default page.
    """
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
    """
    """
    limit, page = limitAndPage(request)

    links = Link.view('public/all',  limit=limit, descending=True, \
                      skip=limit*page)

    return {'links': links, 'page': page, 'limit':limit}


@view_config(route_name='delete_user', logged=True, is_admin=True)
def delete(request):
    """
    """
    user = User.get(request.matchdict['user'])
    user.delete()
    return HTTPFound(location=request.route_url('admin_list', page="0"))


@view_config(route_name='admin', logged=True,  is_admin=True)
def admin(request):
    """
    """
    return HTTPFound(location=request.route_url('admin_list', page="0"))


@view_config(route_name='admin_list', renderer='templates/admin.pt', \
             logged=True, is_admin=True)
def admin_list(request):
    """
    """
    limit, page = limitAndPage(request)

    skip = limit*page
    users = User.view('user/all', skip=skip, limit=limit, descending=True)

    return {'users': users,
            'page': page}

@view_config(route_name='admin_user', renderer='templates/admin_user.pt', \
             logged=True, is_admin=True)
def admin_user(request):
    """
    """
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
    """
    About page.
    """
    return {'project': 'wsgiwars'}

@view_config(route_name='signup', renderer='templates/signup.pt')
def signup(request):
    """
    Signup page.
    """
    return {}

@view_config(route_name='login', renderer='templates/login.pt')
def login(request):
    """
    login page.
    """
    return {}

@view_config(route_name='submitLogin')
def submitLogin(request):
    """
    Action on login page.
    """
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

    if not user.checked:
        request.session.flash(u"please confirm you mail before")
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
    """
    Action on submit page.
    """
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

    if not len(request.POST['password'].strip()) >= 8:
        request.session.flash(u"Password must have at least 8 characters")
        return HTTPFound(location=request.route_path('signup'))

    if request.POST['password'] == request.POST['confirmPassword']:
        password = bcrypt.hashpw(request.POST['password'].encode('utf-8'),
                                 bcrypt.gensalt())

        user = User(password=password,
                    name=request.POST['name'],
                    description=request.POST['description'],
                    mail=request.POST['email'],
                    random=random.randint(1,1000000000),
                    checked = False
                    )
        user._id = request.POST['login']
        user.save()

        if hasattr(request.POST['avatar'], 'filename'):
            tmph, originImage = tempfile.mkstemp(dir=settings['tmp'], \
                                                 suffix="original")
            os.close(tmph)

            tmph, thumbImage = tempfile.mkstemp(dir=settings['tmp'], \
                                                suffix="thumb")
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

        confirm_link = request.route_url('checkLogin',
                userid = user._id,
                randomid = user.random)

        mailer = Mailer()
        message = Message(subject="Your subsription !",
                          sender=settings['mail_from'],
                          recipients=[request.POST['email']],
                          body="Confirm the link\n\n%s" % confirm_link)  # TODO add link

        mailer.send_immediately(message, fail_silently=False)

        return {'name': request.POST['name']}

    else:
        return HTTPFound(location=request.route_path('signup'))


@view_config(route_name='addLink', renderer='templates/addlink.pt', \
             logged=True)
def addlink(request):
    """
    Add a link.
    """
    return {'link': None}

@view_config(route_name='copyLink', renderer='templates/addlink.pt', \
             logged=True)
def copylink(request):
    """
    Copy a link.
    """
    link = Link.get(request.matchdict['link'])

    if link.private:
        raise HTTPNotFound()

    return {'link': link}

@view_config(route_name='submitLink', logged=True)
def submitlink(request):
    """
    Submit a link.
    """
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

    if not link.private:
        user = User.get(request.session['login'])
        user.links[link._id] = link.created
        user.save()

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

    return {'links': links, 'user': user, 'limit': limit, 'page': page}


@view_config(route_name="mylinks", renderer="templates/mylinks.pt", \
             logged=True)
def mylinks(request):
    """
    My link page.
    """
    limit, page = limitAndPage(request)

    links = Link.view('my_link/all', limit=limit,
                      descending=True, skip=page*limit,
                      startkey=[request.session['login'], {}],
                      endkey=[request.session['login']], include_docs=True)

    return {'links': links, 'limit': limit, 'page': page}


@view_config(route_name="tag", renderer="templates/tag.pt")
def tag(request):
    """
    Tag page.
    """
    limit, page = limitAndPage(request)

    links = Link.view('viewTag/all', limit=limit,
                      descending=True, skip=page*limit,
                      startkey=[request.matchdict['tag'], {}],
                      endkey=[request.matchdict['tag']])
    return {'links': links, 'limit': limit, 'page': page}


@view_config(route_name='logout', logged=True)
def logout(request):
    """
    """
    request.session.delete()
    return HTTPFound(location=request.route_path('home'))

@view_config(route_name='rss', renderer='templates/rss.pt')
def rss(request):
    """
    """
    links = Link.view('public/all',  limit=10, descending=True)
    return {'links': links}

@view_config(route_name="tagrss", renderer="templates/tagrss.pt")
def tagrss(request):
    """
    """
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
    """
    """
    link = Link.get(request.matchdict['link'])

    if link.private:
        raise HTTPNotFound()

    return {'link': link}

@view_config(route_name='contacts', renderer='templates/contacts.pt', \
             logged=True)
def contacts(request):
    """
    """
    limit, page = limitAndPage(request)

    users = User.view('viewFollowers/all', limit=limit,
                      descending=True, skip=limit*page,
                      key=request.session['login'])

    return {"users": users, 'limit': limit, 'page': page}

@view_config(route_name='submitContact', \
             renderer='templates/submit_contact.pt', logged=True)
def submitContact(request):
    """
    """
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


@view_config(route_name="unfollow", renderer='templates/unfollow.pt', \
             logged=True)
def unfollow(request):
    """
    Unfollow a contact.
    """
    try:
        user = User.get(request.matchdict['userid'].strip())
    except couchdbkit.exceptions.ResourceNotFound:
        request.session.flash("Sorry, we don't find your buddy.")
        return HTTPFound(location=request.route_path('contacts'))

    return {"user": user}


@view_config(route_name="confirmUnfollow", logged=True)
def confirmUnfollow(request):
    """
    Confirm page to unfollow a contact.
    """
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

@view_config(route_name="profile", renderer='templates/profile.pt', \
             logged=True)
def profile(request):
    """
    View profile page.
    """
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
            mailer = Mailer()
            message = Message(subject="Account deleted",
                             sender=settings['mail_from'],
                             recipients=[user.mail],
                             body="Your account have been deleted")
            mailer.send_immediately(message, fail_silently=False)
            user.delete()
            request.session.delete()
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
    """
    """
    try:
        user = User.get(request.matchdict['userid'].strip())
    except couchdbkit.exceptions.ResourceNotFound:
        raise HTTPNotFound()

    response = Response(content_type='image/jpeg',
                        body=user.fetch_attachment('avatar'))
    return response

@view_config(route_name='comment', renderer='templates/addComment.pt', \
             logged = True)
def comment(request):
    """
    """
    link = Link.get(request.matchdict['link'])
    if request.method == 'POST':
        comment={
                'author' : request.session['login'],
                'date' : datetime.datetime.now(),
                'comment' : request.POST['comment']
                }
        link.comments.append(comment)
        link.save()
        request.session.flash(u"Comment Added!")
    return{'link': link}

@view_config(route_name= 'rmLink', logged=True)
def rmlink(request):
    """
    Delete a link.
    """
    link = Link.get(request.matchdict['link'])

    if not link.private:
        user = User.get(request.session['login'])
        del(user.links[request.matchdict['link']])
        user.save()

    link.delete()

    return HTTPFound(location=request.route_path('mylinks'))

@view_config(route_name= 'rmComment', logged=True)
def rmComment(request):
    """
    Delete a comment.
    """
    link = Link.get(request.matchdict['link'])
    comment = [comment for comment in link.comments if \
            comment['author'] == request.session['login'] and \
            str(comment['date']) == request.matchdict['date']][0]
    link.comments.remove(comment)
    link.save()
    #request.session.flash(u"Unknow Error")
    return HTTPFound(location=request.route_path('comment', link=link._id))

@view_config(route_name='checkLogin', renderer='templates/confirm.pt')
def checkLogin(request):
    """
    Validate inscription
    """
    user = User.get(request.matchdict['userid'])
    if user.checked:
        request.session.flash(u"Already confirmed!")
        return HTTPFound(location=request.route_path('home'))
    if user.random == int(request.matchdict['randomid']):
        return {'user' : user}
    return HTTPFound(location=request.route_path('home'))

@view_config(route_name='submitcheckLogin')
def submitcheckLogin(request):
    """
    submit checklogin
    """
    user = User.get(request.matchdict['userid'])
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

    request.session.flash(u"Welcome %s, you have confirm your account" % user.name)

    user.checked = True
    user.save()

    headers = remember(request, user._id)
    request.session['username'] = user.name
    request.session['login'] = user._id
    request.session['is_admin'] = user.is_admin
    request.session.save()

    return HTTPFound(location=request.route_path('home'), headers=headers)

@view_config(route_name="contactsLinks", renderer="templates/contactslinks.pt", \
             logged=True)
def contactsLinks(request):
    """
    My contacts links.
    """
    limit, page = limitAndPage(request)

    links = Link.view('contacts_links/all', limit=limit,
                      descending=True, skip=page*limit,
                      startkey=[request.session['login'], {}],
                      endkey=[request.session['login']], include_docs=True)

    return {'links': links, 'limit': limit, 'page': page}


@view_config(route_name="cloudTags", renderer="templates/cloudTags.pt")
def cloudTags(request):
    """
    Cloud Tags.
    """

    tmp = Link.view('tags/all',
                    group=True,
                    group_level=1
        )


    tags = {tag['key']: tag['value'] for tag in tmp}

    return {'tags' :tags}
