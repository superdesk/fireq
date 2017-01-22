import datetime as dt
import json
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

import pytest

root = (Path(__file__).parent / '..').resolve()
sys.path.insert(0, str(root))


def pytest_configure():
    tmp = Path('/tmp/fire')
    tmp.mkdir(exist_ok=True)
    conf = {
        'log_root': str(tmp / 'logs'),
        'log_url': 'http://localhost/logs/',
        'domain': 'localhost',
        'url_prefix': ''
    }
    conf = (root / 'config.json').read_text()
    conf = json.loads(conf)
    conf = {
        k: v for k, v in conf.items()
        if k.startswith('github_') or k == 'secret'
    }

    conf_tmp = tmp / 'config.json'
    conf_tmp.write_text(json.dumps(conf, indent=2, sort_keys=True))
    os.environ['FIRE_CONFIG'] = str(conf_tmp)

    _rand = patch('firelib.cli.random').start()
    _rand.randint.return_value = 0

    now = dt.datetime(2017, 1, 1)
    _dt = patch('firelib.cli.dt.datetime').start()
    _dt.now.return_value = now


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
def setup(sp):
    pass


@pytest.fixture
def sp():
    with patch('firelib.cli.subprocess') as sp:
        sp.call.return_value = 0
        yield sp


@pytest.fixture
def main():
    from firelib.cli import main

    return main


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
