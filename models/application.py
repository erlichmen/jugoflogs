from google.appengine.ext import ndb


class Application(ndb.Model):
    secret = ndb.StringProperty(required=True)
