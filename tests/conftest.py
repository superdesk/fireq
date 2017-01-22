import json
import pathlib
import subprocess
import sys
import unittest
from unittest.mock import patch

import pytest

root = (pathlib.Path(__file__).parent / '..').resolve()
sys.path.insert(0, str(root))


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
def setup(request):
    conf = {
        'log_root': '/tmp/fire-logs',
        'log_url': 'http://localhost/logs/',
        'domain': 'localhost',
        'url_prefix': ''
    }
    with patch.dict('api.conf', conf) as conf:
        yield conf


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


@pytest.fixture
def sh():
    def inner(*a, **kw):
        return subprocess.check_output(*a, shell=1, **kw).decode()
    return inner
