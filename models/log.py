from google.appengine.ext import ndb
from google.appengine.api import blobstore
import urllib
import hashlib


class Log(ndb.Model):
    from_user = ndb.StringProperty(required=True)
    created_at = ndb.DateTimeProperty(required=True)
    body = ndb.StringProperty(required=True)
    salt = ndb.StringProperty(required=True)
    links = ndb.StringProperty(repeated=True)

    @property
    def from_user_params(self):
        import email.utils
        return email.utils.parseaddr(self.from_user)

    @property
    def from_user_display_name(self):
        return self.from_user_params[0]

    @property
    def from_user_email(self):
        return self.from_user_params[1]

    def gravatar_url(self, size=None):
        email = self.from_user_email.lower()
        default = "http://www.example.com/default.jpg"
        size = size or 32

        gravatar_url = "http://www.gravatar.com/avatar/" + hashlib.md5(email.lower()).hexdigest() + "?"
        gravatar_url += urllib.urlencode({'d': default, 's': str(size)})

        return gravatar_url

    @property
    def actual_links(self):
        for link in self.links:
            yield 'https://storage.googleapis.com' + link

    @property
    def file_names(self):
        for link in self.links:
            parts = link.split('/')
            yield "/".join(parts[4:])

    @property
    def names_links(self):
        return zip(self.file_names, self.actual_links)
