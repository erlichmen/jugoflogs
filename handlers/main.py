#!/usr/bin/env python
import webapp2
import jinja2
from models import Log
from webapp2_extras import jinja2


class BaseHandler(webapp2.RequestHandler):
    @webapp2.cached_property
    def jinja2(self):
        return jinja2.get_jinja2(app=self.app)

    def render_template(self, filename, **template_args):
        self.response.write(self.jinja2.render_template(filename, **template_args))


class LogsHandler(BaseHandler):
    def get(self, namespace):
        logs = Log.query(namespace=namespace).order(-Log.created_at)
        self.render_template('logs.html', logs=logs)


app = webapp2.WSGIApplication([
    ('/logs/(.*)', LogsHandler)
], debug=True)
