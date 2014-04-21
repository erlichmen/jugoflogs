from google.appengine.ext import ndb
from google.appengine.api import blobstore


class Log(ndb.Model):
    from_user = ndb.StringProperty(required=True)
    created_at = ndb.DateTimeProperty(required=True)
    body = ndb.StringProperty(required=True)
    salt = ndb.StringProperty(required=True)
    links = ndb.StringProperty(repeated=True)

    @property
    def actual_links(self):
        for link in self.links:
            yield 'https://storage.googleapis.com' + link
