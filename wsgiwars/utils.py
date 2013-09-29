import argparse
import ConfigParser

import couchdbkit
from couchdbkit.designer import push

from wsgiwars.models.user import User
from wsgiwars.models.link import Link

def setAdmin():
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

