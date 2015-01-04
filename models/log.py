import base64
import os
from google.appengine.ext import ndb
import urllib
import hashlib
from datetime import datetime


class Log(ndb.Expando):
    from_user = ndb.StringProperty(required=True)

    fullname = ndb.StringProperty(indexed=False)
    email = ndb.StringProperty()
    username = ndb.StringProperty()
    facebookId = ndb.StringProperty()

    created_at = ndb.DateTimeProperty(required=True)
    body = ndb.StringProperty(required=True, indexed=False)

    salt = ndb.StringProperty(required=True)
    links = ndb.StringProperty(repeated=True)

    message_id = ndb.StringProperty()
    parent_id = ndb.StringProperty()

    @property
    def application_name(self):
        return self.key.namespace()

    @classmethod
    def create_salt(cls):
        return base64.urlsafe_b64encode(os.urandom(18))

    @classmethod
    def create(cls, app_name, sender, body=None, created_at=None, message_id=None, parent_id=None, **kwargs):
        return cls(
            namespace=app_name,
            from_user=sender,
            salt=cls.create_salt(),
            created_at=created_at or datetime.utcnow(),
            message_id=message_id,
            parent_id=parent_id,
            body=body.decode(),
            **kwargs)

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