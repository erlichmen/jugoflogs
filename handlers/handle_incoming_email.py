from google.appengine.api import mail
from google.appengine.ext import deferred
from models import Log
import webapp2
from dateutil import parser
from gcs_utilities import enum_message_files


class EmailHandler(webapp2.RequestHandler):
    def get_app_token(self, recipient):
        mail_parts = recipient.split("@")

        if len(mail_parts) != 2:
            raise Exception()

        return mail_parts[0]

    @classmethod
    def store_email(cls, app_name, body):
        message = mail.InboundEmailMessage(body)
        message_id = message.original.get("Message-Id")
        parent_id = message.original.get("In-Reply-To")

        _, body = message.bodies("text/plain").next()

        created_at = parser.parse(message.date)
        created_at = created_at.replace(tzinfo=None)

        log = Log.create(
            app_name,
            message.sender,
            body,
            created_at=created_at,
            message_id=message_id,
            parent_id=parent_id)

        log.links = list(enum_message_files(log, message))

        log.put()

    def post(self, recipient):
        app_token = self.get_app_token(recipient)

        app_name = app_token

        if (len(self.request.body)) < 1024 * 750:
            deferred.defer(EmailHandler.store_email, app_name, self.request.body)
        else:
            EmailHandler.store_email(app_name, self.request.body)


app = webapp2.WSGIApplication([
    ("/_ah/mail/(.+)", EmailHandler),
], debug=True)
