from google.appengine.ext import ndb


class Log(ndb.Model):
    from_user = ndb.StringProperty(required=True)
    created_at = ndb.DateTimeProperty(required=True)
    body = ndb.StringProperty(required=True)
    salt = ndb.StringProperty(required=True)
    links = ndb.StringProperty(repeated=True)
