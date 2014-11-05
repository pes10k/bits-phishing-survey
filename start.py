#!/usr/bin/env python
import config
import tornado.web
import webcommon.server
import bitssurvey.controllers
import os

root_dir = os.path.dirname(os.path.realpath(__file__))
routes = [
    (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": os.path.join(root_dir, "static")}),
    (r"/", bitssurvey.controllers.MainHandler)
]

webcommon.server.start(routes, config)
