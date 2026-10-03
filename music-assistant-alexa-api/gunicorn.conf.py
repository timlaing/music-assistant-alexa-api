"""Clean up ASK subprocesses without replacing Gunicorn worker signal handlers."""

import signal
import sys


def worker_exit(server, worker):
    module = sys.modules.get("app")
    if module is not None:
        module.shutdown_setup_children(signal.SIGTERM)
