"""Stop deployment jobs without replacing Gunicorn worker signal handlers."""

import signal
import sys


def worker_exit(server, worker):
    module = sys.modules.get("app")
    if module is not None:
        module.shutdown_setup_children(signal.SIGTERM)


# OAuth authorization codes must not appear in access logs (omit query strings).
access_log_format = '%(h)s %(l)s %(u)s [%(t)s] "%(m)s %(U)s %(H)s" %(s)s %(b)s %(L)s'
