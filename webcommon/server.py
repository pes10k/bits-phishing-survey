import motor
import tornado.web
import tornado.log
import tornado.httpserver
import pwd
import os
import webcommon.reporting
import datetime

def start(routes, params):

    settings = {
        "log_function": webcommon.reporting.access_request,
        "debug": params.debug,
        "db": motor.MotorClient(**params.mongo_params)[params.mongo_database],
        "start": datetime.datetime.now(),
        "template_path": params.template_path,
        "static_path": "static"
    }

    application = tornado.web.Application(routes, **settings)

    # If we're going to run from a less privilaged user account, we need to
    # find the uid of that user account.  This is needed in several locations,
    # so we can just find it once and hold onto it
    tornado_user = params.tornado_user
    owner_uid = pwd.getpwnam(tornado_user)[2] if tornado_user else None

    # First, make sure that we have a directory set up that we can write logs
    webcommon.reporting.configure(params.log_dir, uid=owner_uid)

    if params.ssl_options:
        server = tornado.httpserver.HTTPServer(
            application, ssl_options=params.ssl_options)
    else:
        server = tornado.httpserver.HTTPServer(application)

    server.listen(params.port)

    # Next, if the config file has specified some lesser user for the
    # application to run as, drop down to that user account now
    if owner_uid:
        os.setuid(owner_uid)
        msg = "Decreasing permisisons to {0}".format(tornado_user)
        tornado.log.app_log.info(msg)

    # Finally, start the server up and start serving requests!
    tornado.ioloop.IOLoop.instance().start()
