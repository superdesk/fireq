import os
import subprocess as sp
import threading
import time

import pytest

from fireq import cli
from fireq.lock import wait_exit


@pytest.fixture(autouse=True)
def reset_terminating():
    cli._terminating.clear()
    yield
    cli._terminating.clear()


def op(status, *paths):
    return {'status': status, 'resources': {'instances': list(paths)}}


def test_lxd_busy_matches_the_instance_and_its_suffixed_containers():
    volume = '/1.0/storage-pools/default/volumes/container/lbpr-1482--build?project=default'
    ops = [
        op('Running', '/1.0/instances/lbpr-1482--www'),
        op('Running', volume),
        op('Running', '/1.0/instances/lbpr-1482'),
    ]

    assert cli.lxd_busy(ops, 'lbpr-1482') == {'lbpr-1482--www', 'lbpr-1482--build', 'lbpr-1482'}


def test_lxd_busy_ignores_other_instances_and_finished_operations():
    ops = [
        op('Success', '/1.0/instances/lbpr-1482--www'),
        op('Running', '/1.0/instances/lbpr-14820--www'),
        op('Running', '/1.0/instances/lbpr-148'),
        {'status': 'Running', 'resources': None},
    ]

    assert cli.lxd_busy(ops, 'lbpr-1482') == set()


def test_stop_jobs_kills_the_whole_job_group(monkeypatch):
    # The autouse `setup` fixture mocks `cli.sp`; this test needs real processes.
    monkeypatch.setattr(cli, 'sp', sp)
    result = {}

    def job():
        result['code'] = cli.sh('sleep 30 & wait', exit=False, quiet=True, isolate=True)

    thread = threading.Thread(target=job)
    thread.start()
    for _ in range(50):
        with cli._jobs_lock:
            pids = list(cli._jobs)
        if pids:
            break
        time.sleep(0.1)
    assert pids, 'job did not start'

    started = time.time()
    cli.stop_jobs(timeout=5)
    thread.join(5)

    assert not thread.is_alive()
    assert time.time() - started < 5
    assert result['code'] != 0
    # The backgrounded sleep shares the job's process group and must be gone too.
    with pytest.raises(ProcessLookupError):
        os.killpg(pids[0], 0)
    assert not cli._jobs


def test_stop_jobs_without_running_jobs_is_a_no_op():
    cli.stop_jobs(timeout=1)

    assert not cli._jobs


def test_wait_exit_returns_once_the_process_is_gone():
    proc = sp.Popen(['sleep', '0.2'])
    reaper = threading.Thread(target=proc.wait)
    reaper.start()

    assert wait_exit(proc.pid, timeout=5)
    reaper.join()


def test_wait_exit_times_out_for_a_live_process():
    proc = sp.Popen(['sleep', '5'])
    try:
        assert not wait_exit(proc.pid, timeout=1)
    finally:
        proc.kill()
        proc.wait()
