from google.appengine.api import mail
from google.appengine.ext import deferred
from google.appengine.api import app_identity
from google.appengine.api import blobstore
from models import Log
import cloudstorage as gcs
import random
import os
import webapp2
from dateutil import parser
import pytz
import base64
import zipfile
import io


class EmailHandler(webapp2.RequestHandler):
    def get_app_token(self, recipient):
        mail_parts = recipient.split('@')

        if len(mail_parts) != 2:
            raise Exception()

        return mail_parts[0]

    @classmethod
    def store_email(cls, app_name, body):
        def enum_files(message):
            for name, content in getattr(message, 'attachments', []):
                if name.endswith('.zip'):
                    with io.BytesIO(content.decode()) as zip_file_data:
                        z = zipfile.ZipFile(zip_file_data)
                        for filename in z.namelist():
                            yield filename, z.read(filename)
                else:
                    yield name, content.decode()

        def create_salt():
            return base64.urlsafe_b64encode(os.urandom(18))

        def create_file(app_name, created_at, salt, name, content):
            default_bucket = app_identity.get_default_gcs_bucket_name()

            write_retry_params = gcs.RetryParams(backoff_factor=1.1)
            key_name = "/%s/%s/%s_%s/%s" % (default_bucket, app_name, created_at.isoformat(), salt, name)
            with gcs.open(key_name, 'w', retry_params=write_retry_params) as gcs_file:
                gcs_file.write(content)

            blobstore_filename = '/gs' + key_name

            return blobstore.create_gs_key(blobstore_filename)

        message = mail.InboundEmailMessage(body)
        salt = create_salt()

        _, body = message.bodies('text/plain').next()

        created_at = parser.parse(message.date)
        created_at = created_at.replace(tzinfo=None)

        log = Log(
            namespace=app_name,
            from_user=message.sender,
            salt=salt,
            created_at=created_at,
            body=body.decode())

        links = []

        for name, data in enum_files(message):
            link = create_file(app_name, created_at, salt, name, data)
            links.append(link)

        log.links = links

        log.put()

    def post(self, recipient):
        app_token = self.get_app_token(recipient)

        app_name = app_token

        deferred.defer(EmailHandler.store_email, app_name, self.request.body)


app = webapp2.WSGIApplication([
    ('/_ah/mail/(.+)', EmailHandler)
], debug=True)
