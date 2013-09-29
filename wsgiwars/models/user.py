import couchdbkit


class User(couchdbkit.Document):
    password = couchdbkit.StringProperty()
    avatar = couchdbkit.StringProperty()
    name = couchdbkit.StringProperty()
    description = couchdbkit.StringProperty()
    is_admin = couchdbkit.BooleanProperty()
    followers = couchdbkit.StringListProperty()
