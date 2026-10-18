"""Stop deployment jobs without replacing Gunicorn worker signal handlers."""

import signal
import sys

# aiohttp's default connection pool keeps idle connections for 15s, while
# gunicorn's default keepalive is only 2s. A request (especially a POST,
# which aiohttp never retries) on a pooled connection gunicorn already
# closed fails with "Server disconnected" or "Connection reset by peer" -
# seen as first-attempt playback failures from Music Assistant, where the
# retry on a fresh connection succeeds (issue #55). 75s exceeds any client
# pool timeout.
keepalive = 75


def worker_exit(_server, _worker):
    module = sys.modules.get("app")
    if module is not None:
        module.shutdown_setup_children(signal.SIGTERM)


# OAuth authorization codes must not appear in access logs (omit query strings).
access_log_format = '%(h)s %(l)s %(u)s [%(t)s] "%(m)s %(U)s %(H)s" %(s)s %(b)s %(L)s'
