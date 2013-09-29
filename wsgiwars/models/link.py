import couchdbkit


class Link(couchdbkit.Document):
#    title = couchdbkit.StringProperty()
    url = couchdbkit.StringProperty()
    created = couchdbkit.DateTimeProperty()
    comment = couchdbkit.StringProperty()
    userID = couchdbkit.StringProperty()
    username = couchdbkit.StringProperty()
    tags = couchdbkit.StringListProperty()
    private = couchdbkit.BooleanProperty()
    comments = couchdbkit.ListProperty()
