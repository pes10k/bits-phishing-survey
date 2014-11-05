"""Main logging functionality for this web service is handled by the
built in tornado logging streams, which in turn is mainly just a set of
configurations for the default python logging system.  This module
just includes some helper functions for customizing the logging system for
the local application, likely fed from the applications config.py file."""

import os
import logging
from logging.handlers import TimedRotatingFileHandler
from tornado.log import access_log, app_log, gen_log
import tornado.options
import tornado.escape

def configure(path, uid=None):
    """Configures the tornado logging streams with application specific
    customizatons, including configuring the application to log to
    the specified directory.

    Throws:
        OSError -- if the given directory doesn't exist and cannot be
                   created, or if it exists but cannot be written to

    Args:
        path -- a directory to create and write logs to

    Keyword Args:
        uid -- If provided, the uid that should own the current, non-rotated
               version of each log is owned by the given system user.
               This is useful if we plan on dropping down to a less
               privilaged user on application run
    """
    # First, create the specified logging directory if it does not already
    # exist.  If we don't have permissions to create the directory,
    # then OSError will be thrown
    if not os.path.isdir(path):
        os.mkdir(path)

    # Next, make sure that the current process has the needed permissions
    # to write to the specified logging directory. If not, throw an
    # exception, to prevent log-less execution
    if not os.access(path, os.W_OK | os.X_OK):
        error = "Unable to write to logging directory {0}".format("path")
        raise OSError(error)

    # Otherwise, if we're sure we can write to the specified logging
    # directory, configure the built in tornado loggers to use that
    # directory instead of the system wide one
    format = "%(created)f|%(message)s"

    tornado_logs = (('access.log', access_log), ('application.log', app_log),
                    ('general.log', gen_log))

    for log_name, logger in tornado_logs:
        log_path = os.path.join(path, log_name)
        handler = TimedRotatingFileHandler(log_path, when="midnight")
        formatter = logging.Formatter(format)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        # Allow application errors to propogate up, so that serious errors
        # can wind up on STDERR or other useful places
        if logger is not app_log:
            logger.propagate = False

        if uid:
            os.chown(log_path, uid, -1)

    tornado.log.enable_pretty_logging()

    # Finally, write a simple start up message, both to test that we're
    # able to write as expected, and to get a start time in the logs
    gen_log.setLevel(logging.INFO)
    gen_log.info("Starting webserver (pid:{0}).".format(os.getpid()))


def access_request(request_handler):
    """Formats each access request tornado receives.  This funciton handles
    formatting the 'message' part (not the timestamp) of the format
    of the loggers configured in the above `configure` function.

    For more information on this functions role and settings, see
    the entry on configuring logging requests in Tornado's online
    documentation:

    http://tornado.readthedocs.org/en/latest/web.html#tornado.web.Application.settings

    """
    status = request_handler.get_status()
    http_request = request_handler.request
    params = {
        'remote_ip': http_request.remote_ip,
        'status': status,
        'method': http_request.method,
        'uri': http_request.uri,
        'protocol': http_request.protocol
    }
    format = "{remote_ip}|{status}|{protocol}|{method}|{uri}".format(**params)
    logging.getLogger("tornado.access").warning(format)


def report_db_error(request_handler, error):
    """Logs and responds to a mongo connection error.  This function handles
    all of the following:
        1) Log the mongo connection error to the application log
        2) Send a standard JSON error message to the connection
        3) Close the HTTP connection

    Args:
        request_handler -- The tornado.web.RequestHandler instance that was
                           responding to the connection request
        error           -- The caught exception, such as a
                           pymongo.errors.AutoReconnect instance
    """
    app_log.error("Mongo connection error: {0}".format(error.message))
    error_result = {
        "data": "Internal Error",
        "error": True
    }
    request_handler.write(tornado.escape.json_encode(error_result))
    request_handler.finish()
