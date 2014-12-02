import tornado.web
from tornado.escape import url_escape
from tornado import gen
import datetime
import config
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


class MainHandler(BaseHandler):

    @tornado.web.asynchronous
    @gen.coroutine
    def get(self):
        token = self.get_argument("token", None)
        if not token:
            raise tornado.web.HTTPError(404, "missing session token")
        doc = {
            "page": "userid",
            "event": "loaded",
            "token": token,
            "timestamp": datetime.datetime.now()
        }
        yield self.settings['db'].events.insert(doc)
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
            self.redirect("/bluestem/login.cgi?token={0}".format(url_escape(token)))
            return

        is_password_page = self.get_argument("ispasswordpage", None)
        if is_password_page:
            doc = {
                "page": "password",
                "event": "password form submitted",
                "token": token,
                "timestamp": datetime.datetime.now()
            }
            yield self.settings['db'].events.insert(doc)
            self.redirect("/survey?token={0}".format(url_escape(token)))
            return

        doc = {
            "page": "userid",
            "event": "userid form submitted",
            "token": token,
            "userid": userid,
            "timestamp": datetime.datetime.now()
        }
        yield self.settings['db'].events.insert(doc)

        doc = {
            "page": "password",
            "event": "loaded",
            "token": token,
            "timestamp": datetime.datetime.now()
        }
        yield self.settings['db'].events.insert(doc)

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
        doc = {
            "page": page,
            "event": event,
            "token": token,
            "timestamp": datetime.datetime.now()
        }
        yield self.settings['db'].events.insert(doc)
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

        doc = {
            "page": "survey",
            "event": "loaded",
            "token": token,
            "timestamp": datetime.datetime.now()
        }
        yield self.settings['db'].events.insert(doc)

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
            Dropdown('did_note_url',
                     _pairs("-", "Yes", "No"),
                     label="Prior to logging in, did you make note of the URL " +
                           "of the page you were logging into?"),
            TextArea('noticed_differences', rows=5, classes=["form-control"],
                     label="If so, did you notice anything different about the " +
                           "URL, compared to the standard URL you use to log " +
                           "into UIC services?"),
            Dropdown('did_notice_logins',
                     _pairs("-", "Yes", "No"),
                     label="During this study, we changed how often "
                           "<em>some</em> participants had to log back in " +
                           "to several popular sites. Did you feel that you " +
                           "had to log in more often than usual?"),
            TextArea('logins_affected_performance', rows=5,
                     classes=["form-control"],
                     label="If you answered yes to #3, do you feel that " +
                           "this contributed to how much time you spent " +
                           "evaluating whether or not to log in to this " +
                           "page?"),
            TextArea('comments', rows=5, classes=["form-control"],
                     label="If you have any other feedback you would like " +
                           "to provide, please include it below."),
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
        if not token:
            raise tornado.web.HTTPError(404, "missing session token")
        doc = {
            "page": "survey",
            "event": "submitted",
            "token": token,
            "did_note_url": self.get_argument("did_note_url", None),
            "noticed_differences": self.get_argument("noticed_differences", None),
            "did_notice_logins": self.get_argument("did_notice_logins", None),
            "logins_affected_performance": self.get_argument("logins_affected_performance", None),
            "comments": self.get_argument('comments', None),
            "email": self.get_argument('email', None),
            "timestamp": datetime.datetime.now()
        }
        yield self.settings['db'].events.insert(doc)
        self.render("survey/complete.html")
