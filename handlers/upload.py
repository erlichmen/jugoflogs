import webapp2
from handlers.base_handler import BaseHandler
from handlers.gcs_utilities import enum_request_files
from google.appengine.api import blobstore
from google.appengine.ext.webapp import blobstore_handlers
import json
from google.appengine.api.app_identity import app_identity
from models import Log


def create_upload_url(application_name):
    return blobstore.create_upload_url(
        "/upload/finish/%s" % application_name,
        gs_bucket_name="%s/%s" % (app_identity.get_default_gcs_bucket_name(), application_name))


class ManualUploadHandler(BaseHandler):
    def get(self, application_name):
        upload_url = create_upload_url(application_name)
        self.render_template('upload.html', upload_url=upload_url)


class UploadHandler(webapp2.RequestHandler):
    def get(self, application_name):
        upload_url = create_upload_url(application_name)

        self.response.headers["Content-Type"] = "application/json"

        self.response.out.write(json.dumps({"upload_url": upload_url}))


class FinishUploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self, application_name):
        log = Log.create(
            application_name,
            self.request.get("sender"),
            self.request.get("body"))

        log.links = list(enum_request_files(log, self.get_file_infos()))

        log.put()

app = webapp2.WSGIApplication([
    ("/upload/finish/(.*)", FinishUploadHandler),
    ("/upload/start/(.*)", UploadHandler),
    ("/upload/manual/(.*)", ManualUploadHandler)
], debug=True)
