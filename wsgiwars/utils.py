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

import argparse
import ConfigParser

import couchdbkit
from couchdbkit.designer import push

from wsgiwars.models.user import User
from wsgiwars.models.link import Link

def setAdmin():
    """
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--conf',
                        help='wsgi conf file')

    parser.add_argument('--userid',
                        help='user id')

    args = parser.parse_args()

    config = ConfigParser.RawConfigParser()
    config.read(args.conf)

    server = couchdbkit.Server(config.get('app:main', 'couchdb.url'))
    db = server.get_or_create_db(config.get('app:main','couchdb.db'))
    User.set_db(db)

    try:
        user = User.get(args.userid)
        user.is_admin = True
        user.save()

        print "%s is now admin" % args.userid
    except couchdbkit.exceptions.ResourceNotFound:
        print "%s not found" % args.userid


def delAndPurge():
    """
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--conf',
                        help='wsgi conf file')

    parser.add_argument('--userid',
                        help='user id')

    args = parser.parse_args()

    config = ConfigParser.RawConfigParser()
    config.read(args.conf)

    server = couchdbkit.Server(config.get('app:main', 'couchdb.url'))
    db = server.get_or_create_db(config.get('app:main','couchdb.db'))

    User.set_db(db)
    Link.set_db(db)


    push('couchdb/_design/purge', db)

    try:
        user = User.get(args.userid)
        user.delete()

        print "%s is now deleted" % args.userid
    except couchdbkit.exceptions.ResourceNotFound:
        print "%s not found" % args.userid

    links = Link.view('purge/all',
                      key=args.userid,
                      include_docs=True)

    print "%d links found" % len(links)

    for link in links:
        link.delete()

    print "job done"

