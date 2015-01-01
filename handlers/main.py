#!/usr/bin/env python
from google.appengine.ext import ndb
import webapp2
from handlers.base_handler import BaseHandler
from models import Log


class LogsHandler(BaseHandler):
    def get(self, namespace):
        logs = Log.query(namespace=namespace).order(-Log.created_at)
        self.render_template('logs.html', logs=logs, namespace=namespace)


class ViewerHandler(BaseHandler):
    def get(self, namespace, log_key, name):
        log = ndb.Key(urlsafe=log_key, namespace=namespace).get()
        self.render_template('viewer.html', log=log)


app = webapp2.WSGIApplication([
    ('/logs/(.*?)/view/(.*?)/(.*)', ViewerHandler),
    ('/logs/(.*)', LogsHandler)
], debug=True)
