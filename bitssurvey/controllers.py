import tornado.web
from tornado import gen
import datetime
import config


class BaseHandler(tornado.web.RequestHandler):

    def prepare(self):
        # If we're not in debugging mode (ie we're in "production"),
        # send down HTTP Strict Transport Security header to make sure
        # we're only visited via https
        if not config.debug:
            self.set_header('Strict-Transport-Security',
                            'max-age=16070400; includeSubDomains')
        super(BaseHandler, self).prepare()


class MainHandler(BaseHandler):
    TEMPLATE = "signin/userid.html"

    def get(self):
        self.render(MainHandler.TEMPLATE)
