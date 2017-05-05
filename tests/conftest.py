import datetime as dt
import json
import os
import re
import shlex
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

import pytest

root = (Path(__file__).parent / '..').resolve()
sys.path.insert(0, str(root))


def pytest_configure():
    tmp = Path('/tmp/fireq')
    tmp.mkdir(exist_ok=True)
    conf = root / 'config.json'
    if conf.exists():
        conf = conf.read_text()
        conf = json.loads(conf)
        conf = {
            k: v for k, v in conf.items()
            if k.startswith('github_') or k == 'secret'
        }
    else:
        conf = {
            'secret': '11111111111111111111111111111111',
            'github_basic': '',
        }

    conf_tmp = tmp / 'config.json'
    conf_tmp.write_text(json.dumps(conf, indent=2, sort_keys=True))
    os.environ['FIRE_CONFIG'] = str(conf_tmp)

    _rand = patch('fireq.cli.random').start()
    _rand.randint.return_value = 0

    now = dt.datetime(2017, 1, 1)
    _dt = patch('fireq.cli.dt.datetime').start()
    _dt.now.return_value = now

    # lock is working when running from shell
    patch('fireq.lock').start()


def pytest_addoption(parser):
    parser.addoption(
        '--slow', action='store_true',
        help='Also run slow tests'
    )
    parser.addoption(
        '--real-http', action='store_true',
        help='Also run tests with real http requests'
    )


@pytest.fixture
def slow(request):
    if not request.node.config.getvalue('slow'):
        raise unittest.SkipTest('slow')


@pytest.fixture
def real_http(request):
    if not request.node.config.getvalue('real_http'):
        raise unittest.SkipTest('real http')


@pytest.fixture
def setup(sp, gh_call):
    pass


@pytest.fixture
def sp():
    with patch('fireq.cli.sp') as sp:
        sp.call.return_value = 0
        yield sp


@pytest.fixture
def gh_call(load_json):
    def fn(url, *a, **kw):
        # it uses in gh.get_sha
        if re.findall(r'git/refs/', url):
            return load_json('gh_sha-sds_master.json')
        return mok

    p = patch('fireq.gh.call', wraps=fn)
    mok = p.start()
    mok._stop = p.stop
    yield mok
    try:
        mok._stop()
    except RuntimeError:
        pass


@pytest.fixture
def main():
    from fireq.cli import main

    def inner(str_args):
        args = shlex.split(str_args)
        return main(args)
    return inner


@pytest.fixture
def raises():
    return pytest.raises


def _load(path):
    return (root / 'tests/fixtures' / path).read_text()


@pytest.fixture
def load():
    return _load


@pytest.fixture
def load_json():
    def inner(path):
        txt = _load(path)
        return json.loads(txt)
    return inner
