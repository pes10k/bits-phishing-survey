#!/usr/bin/env python3
import config
import tornado.web
import webcommon.server
import bitssurvey.controllers
import os

root_dir = os.path.dirname(os.path.realpath(__file__))
static_path = os.path.join(root_dir, "static")

routes = [
    (r"/", bitssurvey.controllers.MainHandler),
    (r"/bluestem/login.cgi", bitssurvey.controllers.SubmitHandler),
    (r"/events", bitssurvey.controllers.EventHandler),
    (r"/survey", bitssurvey.controllers.SurveyHandler),
]

webcommon.server.start(routes, config)
