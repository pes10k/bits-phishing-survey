#!/usr/bin/env python
import config
import tornado.web
import webcommon.server
import bitssurvey.controllers
import os

root_dir = os.path.dirname(os.path.realpath(__file__))
static_path = os.path.join(root_dir, "static")

routes = [
    (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": static_path}),
    (r"/", bitssurvey.controllers.MainHandler),
    (r"/bluestem/login.cgi", bitssurvey.controllers.SubmitHandler),
    (r"/events", bitssurvey.controllers.EventHandler),
    (r"/survey", bitssurvey.controllers.SurveyHandler),
]

webcommon.server.start(routes, config)
