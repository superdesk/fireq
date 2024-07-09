"""CI server with dashboard and webhook handler

It mainly transfers web requests to proper call of "./fire" in background.
"""
import asyncio
import datetime as dt
import hashlib
import hmac
import json
import os
import re
import uuid
import warnings
from pathlib import Path

from aiohttp import web, ClientSession
from aioauth_client import GithubClient
from aiohttp_session import get_session, session_middleware
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from pystache import render

from . import log, conf, root, pretty_json, get_restart_url, gh
from .cli import scopes, Ref

about = '''
<head>
<title>Fireq Continuous Integration</title>
    <link rel="icon" type="image/png" href="/html/theme/favicon.ico" sizes="16x16">
<style>
 body, h3>a {
    font-family: ui-monospace,SFMono-Regular,SF Mono,Menlo,Consolas,Liberation Mono,monospace !important;
    max-width: none !important;
    text-decoration: none !important;
   }
 img#logo {
    margin: 0 3px -4px 1px;
   }
 h3>a:hover {
    text-decoration: none;
    border-bottom: 2px solid currentColor;
   }
 b.name {
    font-size: 100%;
    display: inline-block;
    width: 15rem;
   }
</style>
</head>
<h3><a title="Fireq Continuous Integration system" href="https://github.com/superdesk/fireq/blob/master/docs/ci.md" target="_blank">
    Fireq<img src="/html/theme/fire_1f525.gif" alt="fireq-lxd" id="logo">CI
</a></h3>
'''


def get_app():
    middlewares = [
        session_middleware(EncryptedCookieStorage(conf['secret'].encode())),
        auth_middleware
    ]
    app = web.Application(middlewares=middlewares)
    init_loop(app.loop)

    def remove_ts(handler):
        async def inner(request):
            if request.match_info.get('trailing_slash'):
                return web.HTTPFound(request.path[:-1])
            if asyncio.iscoroutinefunction(handler):
                return await handler(request)
            return handler(request)
        return inner

    def url(path, handler, **kw):
        method = kw.pop('method', 'GET')
        if not path.endswith('/'):
            path = path + r'{trailing_slash:[/]?}'
            handler = remove_ts(handler)

        path = conf['url_prefix'] + path
        return app.router.add_route(method, path, handler, **kw)

    url('/', index)
    url('/login', login)
    url('/logs/{path:.*}', logs)
    url('/hook', hook, method='POST')

    prefix = '{prefix:(%s)}' % '|'.join(i.name for i in scopes)
    url(r'/%s' % prefix, repo)
    url(r'/%s/{ref:.+}/restart' % prefix, restart)

    # TODO: previous urls; keep redirects for a while
    refs_prefix = {'pr': 'pull/', 'br': 'heads/'}
    url(
        r'/%s/restart/{typ:(pr|br)}/{ref:.+}' % prefix,
        lambda r: web.HTTPFound(get_restart_url(
            r.match_info['prefix'],
            refs_prefix[r.match_info['typ']] + r.match_info['ref']
        ))
    )
    url('/push/{p:.*}',
        lambda r: web.HTTPFound('/logs/0/' + r.match_info['p']))
    return app


async def auth_middleware(app, handler):
    """ Login via Github """
    def gh_client(**kw):
        return GithubClient(client_id=conf['github_id'], client_secret=conf['github_secret'], **kw)

    async def callback(request):
        session = await get_session(request)
        log.debug('callback: session=%s GET=%s', session, request.query_string)
        if session.get('github_state') != request.query.get('state'):
            return web.HTTPBadRequest()
        code = request.url.query['code']
        if not code:
            return web.HTTPBadRequest()

        gh = gh_client()
        token, _ = await gh.get_access_token(code)
        gh = gh_client(access_token=token)
        req = await gh.request('GET', 'user')
        user = req
        log.debug('user: %s \n\n', user)
        users = []
        for org in conf['github_orgs']:
            _, resp = await gh_api('orgs/%s/members?per_page=100' % org)
            users.extend(u['login'] for u in resp)
        log.debug('members %s: %s', len(users), users)
        log.debug('login: %s\n\n', user.get('login'))
        if user.get('login') in users:
            session['login'] = user.get('login')
            session.pop('github_state', None)
            session.pop('github_url', None)
            location = session.pop('location')
            return web.HTTPFound(location)
        return web.HTTPForbidden()

    async def check_auth(request):
        session = await get_session(request)
        login = session.get('login')
        if login:
            request['login'] = login
            return await handler(request)
        elif 'github_state' not in session:
            gh = gh_client()
            state = str(uuid.uuid4())
            url = gh.get_authorize_url(scope='', state=state)
            session['github_state'] = state
            session['github_url'] = url
            session['location'] = request.path
            log.debug('check_auth: %s', session)
        return web.HTTPFound(conf['url_prefix'] + '/login')

    async def inner(request):
        if request.path == (conf['url_prefix'] + conf['github_callback']):
            return await callback(request)
        elif request.path == (conf['url_prefix'] + '/hook'):
            return await handler(request)
        elif request.path == (conf['url_prefix'] + '/login'):
            return await handler(request)
        else:
            return await check_auth(request)

    return inner


async def login(request):
    session = await get_session(request)
    log.debug('login: %s', session)
    if 'github_url' not in session:
        return web.HTTPFound(conf['url_prefix'] + '/')

    ctx = {'login_url': session['github_url']}
    return render_tpl(login_tpl, ctx)
login_tpl = '''
<p><a href="{{login_url}}">Login via Github</a></p>
<p>
You should be a member of
<a href="https://github.com/orgs/superdesk/people">Superdesk Organization</a>
</p>
'''


async def logs(request):
    path = '/.logs/%s' % request.match_info['path']
    return web.HTTPOk(
        headers=[('X-Accel-Redirect', path)],
        content_type='text/html' if path.endswith('.htm') else 'text/plain',
    )


def get_hook_ctx(headers, body, **extend):
    event = headers.get('X-Github-Event')
    if event == 'pull_request':
        if body['action'] not in ('opened', 'reopened', 'synchronize'):
            log.info('skip %s:%s', event, body['action'])
            return
        ref = 'pull/%s' % body['number']
        sha = body['pull_request']['head']['sha']
    elif event == 'push':
        sha = body['after']
        ref = re.sub('^refs/', '', body['ref'])
    else:
        log.info('skip %s', event)
        return

    # mean it has been deleted
    if sha == '0000000000000000000000000000000000000000':
        log.info('skip %s: %s deleted', event, ref)
        return

    repo = body['repository']['full_name']
    scope = [i.name for i in scopes if i.repo == repo]
    if not scope:
        log.info('skip %s: repo=%s', event, repo)
        return

    ref = Ref(scope[0], ref, '<sha>')
    if not [1 for p in ('heads/', 'pull/') if ref.val.startswith(p)]:
        log.info('Skip ref: %s', ref)
        return

    log_path = (
        'hooks/{time:%Y%m%d-%H%M%S}-{event}-{uid}-{sha}.json'
        .format(uid=ref.uid, time=dt.datetime.now(), sha=sha, event=event)
    )
    log_file = Path(conf['log_root']) / log_path
    log_file.parent.mkdir(parents=True, exist_ok=True)
    log_file.write_text(pretty_json([headers, body]))
    log_url = conf['log_url'] + log_path
    log.info('%s request=%s', ref, log_url)
    return ref


async def hook(request):
    body = await request.read()
    check_signature = hmac.compare_digest(
        get_signature(body),
        request.headers.get('X-Hub-Signature', '')
    )
    if not check_signature:
        return web.HTTPBadRequest()

    body = await request.json()
    headers = dict(request.headers.items())
    del headers['X-Hub-Signature']
    ref = get_hook_ctx(headers, body, clean=True)
    if ref:
        request.app.loop.create_task(ci(ref))
    return web.json_response(ref)


async def restart(request):
    prefix = request.match_info['prefix']
    try:
        repo = getattr(scopes, prefix).name
    except AttributeError:
        return web.HTTPNotFound()

    ref = request.match_info['ref']
    ref = Ref(repo, ref, '<sha>')
    targets = request.query.get('t', '').split(',')
    all = request.query.get('all')

    request.app.loop.create_task(ci(ref, targets, all))
    await asyncio.sleep(2)
    log_url = '%slatest/%s/' % (conf['log_url'], ref.uid)
    return web.HTTPFound(log_url)


async def index(request):
    ctx = {'repos': [{'short': i.name, 'name': i.repo} for i in scopes]}
    return render_tpl(index_tpl, ctx)
index_tpl = '''
<ul>
{{#repos}}
    <li><a href="{{short}}">{{name}}</a></li>
{{/repos}}
</ul>
'''


LOGS_PATH = '/var/log/fire/3/latest/'

FAILURE_FILES = (
    '!failure-build.json',
    '!failure-www.json',
)

SUCCESS_FILES = (
    '!success-build.json',
    '!success-www.json'
)


def set_build_status(item):
    """Get latest build status, 0 - OK, 1 - Failure, 2 - Pending"""
    def file_status(files):
        return [os.path.exists(os.path.join(LOGS_PATH, item['lxc'], filename)) for filename in files]

    if all(file_status(SUCCESS_FILES)):
        item['status_ok'] = True
        return

    if any(file_status(FAILURE_FILES)):
        item['status_failure'] = True
        return

    item['status_pending'] = True


async def repo(request):
    prefix = request.match_info['prefix']
    try:
        repo_name = getattr(scopes, prefix).repo
    except AttributeError:
        return web.HTTPNotFound()

    def info(name, pr=False):
        ref = '%s/%s' % ('pull' if pr else 'heads', name)
        if pr:
            lxc = '%spr-%s' % (prefix, name)
            gh_url = 'https://github.com/%s/pull/%s' % (repo_name, name)
        else:
            name_cleaned = re.sub('[^a-z0-9]', '', name.lower())
            lxc = '%s-%s' % (prefix, name_cleaned)
            gh_url = 'https://github.com/%s/commits/%s' % (repo_name, ref)

        _info = {
            'protected_db': lxc in conf['protected_dbs'],
            'name': name,
            'lxc': lxc,
            'gh_url': gh_url,
            'url': 'http://%s.%s' % (lxc, conf['domain']),
            'restart_url': get_restart_url(prefix, ref),
            'logs_url': '%slatest/%s/' % (conf['log_url'], lxc),
        }

        set_build_status(_info)
        return _info

    resp, body = await gh_api('repos/%s/pulls?per_page=100' % repo_name)
    pulls = [info(i['number'], True) for i in body]

    resp, body = await gh_api('repos/%s/branches?per_page=100' % repo_name)
    branches = [info(i['name']) for i in body]

    refs = [
        {'title': 'Pull requests', 'items': pulls},
        {'title': 'Branches', 'items': branches}
    ]
    return render_tpl(repo_tpl, {'refs': refs})
repo_tpl = '''
{{#refs}}
<h3>{{title}}</h3>
<ul>
{{#items}}
    <li>
        <b class="name">{{name}}</b>
        <a href="{{url}}"
		{{#status_ok}}
		style="color:green"
		{{/status_ok}}
		{{#status_failure}}
		style="color:red"
		{{/status_failure}}
		{{#status_pending}}
		style="color:orange"
		{{/status_pending}}
	>[instance]</a>
        <a href="{{gh_url}}" style="color:gray">[github]</a>
        <a href="{{logs_url}}" style="color:black">[latest logs]</a>
        <a href="{{restart_url}}?t=www" style="color:black">[deploy]</a>
        <a href="{{restart_url}}" style="color:black">[restart]</a>
        <a href="{{restart_url}}?all=1" style="color:black">[restart all]</a>
        {{#protected_db}}
        <i style="color:grey">protected db</i>
        {{/protected_db}}
        {{^protected_db}}
        <a href="{{restart_url}}?t=reset"
            style="color:black"
            onclick="return confirm('Reseting db for {{lxc}}. Are you sure?')"
        >[reset db]</a>
        {{/protected_db}}
    </li>
{{/items}}
</ul>
{{/refs}}
'''


async def ci(ref, targets=None, all=False):
    targets = ' '.join('-t %s' % t for t in targets or [] if t)
    cmd = (
        'cd {root} && '
        'FIRE_UID={uid} ./fire ci {ref.scope.name} {ref.val} {all} {targets}'
        .format(
            root=root,
            ref=ref,
            uid=str(uuid.uuid4().hex[:8]),
            targets=targets,
            all=(all and '--all' or '')
        )
    )
    log.info(cmd)
    proc = await asyncio.create_subprocess_shell(cmd, executable='/bin/bash')
    code = await proc.wait()
    log.info('code=%s: %s', code, cmd)
    return code


async def gh_api(url, data=None):
    if not url.startswith('https://'):
        url = 'https://api.github.com/' + url

    async with ClientSession(headers=gh.auth()) as s:
        if data is None:
            method = 'GET'
        else:
            method = 'POST'
            data = json.dumps(data)
        async with s.request(method, url, data=data) as resp:
            return resp, await resp.json()


def get_signature(body):
    sha1 = hmac.new(conf['secret'].encode(), body, hashlib.sha1).hexdigest()
    return 'sha1=' + sha1


def init_loop(loop=None):
    if not loop:
        loop = asyncio.get_event_loop()

    if conf['debug_aio']:
        # Enable debugging
        loop.set_debug(True)

        # Make the threshold for "slow" tasks very very small for
        # illustration. The default is 0.1, or 100 milliseconds.
        loop.slow_callback_duration = 0.001

        # Report all mistakes managing asynchronous resources.
        warnings.simplefilter('always', ResourceWarning)
    return loop


def render_tpl(tpl, ctx, status=200, content_type='text/html'):
    tpl = about + tpl
    resp = web.Response(text=render(tpl, ctx))
    resp.content_type = content_type
    resp.set_status(status)
    return resp


app = get_app()
if __name__ == '__main__':
    web.run_app(app, port=os.environ.get('PORT', 8080))
