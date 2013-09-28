import couchdbkit


class User(couchdbkit.Document):
    password = couchdbkit.StringProperty()
    avatar = couchdbkit.StringProperty()
    name = couchdbkit.StringProperty()
    description = couchdbkit.StringProperty()
