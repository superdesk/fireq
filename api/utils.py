import base64
import hashlib
import hmac
import json

from . import conf


def gh_auth():
    b64auth = base64.b64encode(conf['github_auth'].encode()).decode()
    headers = {'Authorization': 'Basic %s' % b64auth}
    return headers


def get_signature(body):
    sha1 = hmac.new(conf['secret'].encode(), body, hashlib.sha1).hexdigest()
    return 'sha1=' + sha1


def get_restart_url(short_name, ref):
    return (
        'https://{domain}{url_prefix}/{short_name}/{ref}/restart'
        .format(
            domain=conf['domain'],
            url_prefix=conf['url_prefix'],
            short_name=short_name,
            ref=ref
        )
    )


def pretty_json(obj):
    return json.dumps(obj, indent=2, sort_keys=True)
