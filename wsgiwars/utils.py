import argparse
import ConfigParser

import couchdbkit

from wsgiwars.models.user import User

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
