import contextlib
import os
import signal
import socket
import subprocess as sp
import time

from . import log


def wait_exit(pid, timeout):
    """Wait until process `pid` has exited, at most `timeout` seconds."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return True
        time.sleep(1)
    return False


@contextlib.contextmanager
def kill_previous(name, timeout=180):
    # try to kill previous process by socket name
    # inspired by http://stackoverflow.com/a/7758075
    cmd = 'ss -a | grep -oE "%s[0-9]+" || true' % name
    txt = sp.check_output(cmd, shell=True)
    if txt:
        pid = int(txt.decode().rsplit(':', 1)[1])
        try:
            os.kill(pid, signal.SIGTERM)
            # The previous run stops its jobs before exiting; a fixed short
            # sleep let both runs work on the same containers at once.
            if not wait_exit(pid, timeout):
                log.error('previous run pid=%s still alive after %ss', pid, timeout)
        except Exception as e:
            log.exception(e)

    sock0 = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    sock1 = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    try:
        # next line fails if previous proccess is still running
        sock0.bind('\0' + name)
        # write pid information to another socket
        sock1.bind('\0' + name + str(os.getpid()))
        yield
    except socket.error as e:
        log.exception(e)
        raise SystemExit(1)
    finally:
        sock0.close()
        sock1.close()
