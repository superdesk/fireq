import base64
import json
import re
import time
import urllib.error
import urllib.request

from . import conf, log, pretty_json

started = {}


class Error(Exception):
    pass


def auth():
    b64auth = base64.b64encode(conf['github_auth'].encode()).decode()
    headers = {'Authorization': 'Basic %s' % b64auth}
    return headers


def call(url, data=None):
    if not url.startswith('https://'):
        url = 'https://api.github.com/' + url
    try:
        method = None
        if data is not None:
            method = 'POST'
            data = json.dumps(data).encode()
        req = urllib.request.Request(url, headers=auth(), method=method)
        res = urllib.request.urlopen(req, data=data)
        log.debug('%s url=%r', res.status, url)
        return json.loads(res.read().decode())
    except urllib.error.URLError as e:
        log.error(
            '%s, code=%s url=%r \nposted_data=%s\nerror=%s',
            e,
            e.code,
            url,
            pretty_json(data),
            pretty_json(e.fp.read()),
        )
        raise Error(e)


def get_sha(ref):
    repo = ref.scope.repo
    ref = ref.val + ('/head' if ref.is_pr else '')
    resp = call('repos/{0}/git/refs/{1}'.format(repo, ref))
    return resp['object']['sha']


def _post_status(url, context, state, target_url, desc, logs):
    data = {
        'context': conf['status_prefix'] + context,
        'state': state,
        'target_url': target_url,
        'description': desc,
    }
    if conf['no_statuses']:
        data.update({'!': 'wasn\'t sent to Github'})
    else:
        data = call(url, data)
    logs.file('!%s-%s.json' % (state, context)).write_text(pretty_json(data))


def post_status(target, ctx, logs, *, code=None, pending_url=None):
    global started
    state = {
        None: 'pending',
        0: 'success',
        1: 'failure'
    }[code and 1]

    desc = ''
    url = logs.url(target + '.log')
    if state == 'pending':
        started[target] = time.time()
        if pending_url:
            desc = 'waiting for start'
            url = pending_url
    else:
        if started.get(target):
            elapsed = (time.time() - started[target])
            desc = 'duration: %dm%ds' % (elapsed // 60, elapsed % 60)
        url = url + '.htm'

    if target == 'www' and code == 0:
        url = 'http://' + ctx['host']
        desc = 'click "Details" to see the test instance'
    elif target == 'build' and pending_url:
        post_status('restart', ctx, logs, code=0)
    elif target == 'restart':
        url = ctx['restart_url']
        desc = 'click "Details" to restart the build'

    _post_status(
        'repos/{repo_name}/statuses/{repo_sha}'.format(**ctx),
        target, state, url, desc, logs
    )


def clean_statuses(ref, targets, logs):
    if conf['no_statuses']:
        return
    targets = targets + ['restart']
    body = call('repos/{0.scope.repo}/commits/{0.sha}/status'.format(ref))
    url = 'repos/{0.scope.repo}/statuses/{0.sha}'.format(ref)
    for s in body['statuses']:
        pattern = r'^%s' % re.escape(conf['status_prefix'])
        if not re.search(pattern, s['context']):
            continue
        context = re.sub(pattern, '', s['context'])
        if context in targets:
            continue
        desc = 'cleaned, is not presented anymore'
        _post_status(url, context, 'success', logs.url(), desc, logs)
