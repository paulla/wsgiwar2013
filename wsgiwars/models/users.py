import couchdbkit


class Users_db(couchdbkit.Document):
    _id = couchdbkit.StringProperty()
    password = couchdbkit.StringProperty()
    avatar = couchdbkit.StringProperty()
    name = couchdbkit.StringProperty()
    description = couchdbkit.StringProperty()
