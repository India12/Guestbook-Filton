from google.appengine.ext import ndb

class Message(ndb.Model):
    name = ndb.StringProperty()
    surname = ndb.StringProperty()
    text = ndb.TextProperty()
    email = ndb.StringProperty()
    dateTime = ndb.DateTimeProperty(auto_now_add=True)
    deleted = ndb.BooleanProperty(default=False)
