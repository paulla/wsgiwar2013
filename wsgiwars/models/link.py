import couchdbkit


class Links_db(couchdbkit.Document):
    title = couchdbkit.StringProperty()
    url = couchdbkit.StringProperty()
    created = couchdbkit.DateTimeProperty()
    tags = couchdbkit.StringProperty()
