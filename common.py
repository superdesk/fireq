import base64
import json
import logging
import re
import subprocess
import urllib.request
import urllib.error
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
        ('sdbase', 'base-sd'),
        ('domain', 'localhost'),
        ('logurl', lambda c: 'http://%s/' % c['domain']),
        ('e2e_count', 4),
        ('cpus_per_lxc', 3),
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


def gh_api(url, exc=True):
    if not url.startswith('https://'):
        url = 'https://api.github.com/repos/' + url
    try:
        req = urllib.request.Request(url, headers=gh_auth())
        res = urllib.request.urlopen(req)
        res = json.loads(res.read().decode())
        return res
    except urllib.error.URLError as e:
        if exc:
            raise
    return None


def sd_containers(opts=''):
    names = subprocess.check_output('lxc-ls -1 %s' % opts, shell=True)
    names = names.decode().split()
    return (n for n in names if re.match('^sd[a-z]*-[a-z0-9]+$', n))


def pretty_json(obj):
    return json.dumps(obj, indent=2, sort_keys=True)
