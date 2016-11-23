import base64
import json
import logging
from pathlib import Path

log = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.DEBUG,
    datefmt='%H:%M:%S',
    format='%(asctime)s %(message)s'
)
root = Path(__file__).resolve().parent


def get_conf():
    conf = (root / 'config.json').read_text()
    conf = json.loads(conf)

    defaults = [
        ('debug', False),
        ('debug_aio', False),
        ('sdbase', 'sdbase'),
        ('domain', 'localhost'),
        ('logurl', lambda c: 'http://%s/' % c['domain']),
        ('e2e_count', 4),
    ]
    for key, value in defaults:
        if callable(value):
            value = value(conf)
        conf.setdefault(key, value)
    return conf

conf = get_conf()


def gh_auth():
    b64auth = base64.b64encode(conf['github_auth'].encode()).decode()
    headers = {'Authorization': 'Basic %s' % b64auth}
    return headers


def pretty_json(obj):
    return json.dumps(obj, indent=2, sort_keys=True)
