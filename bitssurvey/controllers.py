import tornado.web
from tornado.escape import url_escape
from tornado import gen
import datetime
import config
from base64 import b64decode
import pybootstrapforms.form
from pybootstrapforms.inputs import Field, Dropdown, TextArea, Markup


class BaseHandler(tornado.web.RequestHandler):

    def prepare(self):
        # If we're not in debugging mode (ie we're in "production"),
        # send down HTTP Strict Transport Security header to make sure
        # we're only visited via https
        if not config.debug:
            self.set_header('Strict-Transport-Security',
                            'max-age=16070400; includeSubDomains')
        super(BaseHandler, self).prepare()

    def record_event(self, page, event, token, **kwargs):
        doc = {
            "page": page,
            "event": event,
            "token": b64decode(token),
            "timestamp": datetime.datetime.now()
        }
        for key, value in kwargs.items():
            doc[key] = value
        db = self.settings['db']
        yield db.events.insert(doc)


class MainHandler(BaseHandler):

    def get(self):
        token = self.get_argument("token", None)
        if not token:
            raise tornado.web.HTTPError(404, "missing session token")
        self.render("signin/userid.html", params={"token": token}, token=token)


class SubmitHandler(BaseHandler):

    @tornado.web.asynchronous
    @gen.coroutine
    def post(self):
        token = self.get_argument("token", None)
        if not token:
            raise tornado.web.HTTPError(404, "missing session token")

        userid = self.get_argument("UserID", None)
        if not userid:
            self.redirect("/?token={0}".format(url_escape(token)))
            return

        is_password_page = self.get_argument("ispasswordpage", None)
        if is_password_page:
            self.record_event("password", "password form submitted", token)
            self.redirect("/survey?token={0}".format(url_escape(token)))
            return

        self.record_event("userid", "userid form submitted", token,
                          userid=userid)

        template_params = {
            "params": {"token": token},
            "token": token,
            "userid": userid
        }
        self.render("signin/password.html", **template_params)


class EventHandler(BaseHandler):

    @tornado.web.asynchronous
    @gen.coroutine
    def post(self):
        page = self.get_argument("page")
        event = self.get_argument("event")
        token = self.get_argument("token")
        print "START WTITE"
        self.record_event(page, event, token)
        print "FIN WRITE"
        self.finish()


class SurveyHandler(BaseHandler):

    @tornado.web.asynchronous
    @gen.coroutine
    def get(self):
        token = self.get_argument("token", None)
        if not token:
            raise tornado.web.HTTPError(404, "missing session token")

        def _pairs(*items):
            return tuple(((v, v) for v in items))

        self.record_event("survey", "loaded", token)

        fields = [
            Dropdown('browser', _pairs("-", "Chrome", "Firefox"),
                     label="What browser did you use during this survey?"),
            Dropdown('problems', _pairs("-", "Yes", "No"),
                     label="Did you encoutner any technical problems during " +
                           "this study?"),
            Dropdown('affiliation',
                     _pairs("-", "Faculty", "Staff", "Student", "Other"),
                     label="Which option best describes your affiliation " +
                           "with UIC"),
            TextArea('comments', rows=5, classes=["form-control"],
                     label="Do you have any other feedback you would like " +
                           "to provide."),
            Field('email', label="Email Address",
                  help="What email address should we use if we need to " +
                       "follow up?"),
            Markup("<input type='hidden' name='token' value='{0}' />".format(token))
        ]

        form = pybootstrapforms.form.Form("End of Study Survey", *fields)
        params = {
            "form": form,
            "token": token
        }
        self.render("survey/form.html", **params)

    @tornado.web.asynchronous
    @gen.coroutine
    def post(self):
        token = self.get_argument("token", None)
        comments = self.get_argument("comments", "")
        if not token:
            raise tornado.web.HTTPError(404, "missing session token")
        self.record_event("survey", "submitted", token, comments=comments)
        self.render("survey/complete.html")
