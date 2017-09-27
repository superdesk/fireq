import contextlib
import os
import signal
import socket
import subprocess as sp
import time

from . import log


@contextlib.contextmanager
def kill_previous(name):
    # try to kill previous process by socket name
    # inspired by http://stackoverflow.com/a/7758075
    cmd = 'ss -a | grep -oE "%s[0-9]+" || true' % name
    txt = sp.check_output(cmd, shell=True)
    if txt:
        pid = int(txt.decode().rsplit(':', 1)[1])
        try:
            os.kill(pid, signal.SIGTERM)
            # wait a bit when process and related containers will be cleaned
            time.sleep(10)
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
