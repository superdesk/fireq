#!/usr/bin/env python3
import asyncio
import hashlib
import hmac
import os
import re
import uuid
import warnings

# from aiofiles import open as async_open
from aiohttp import web
from aioauth_client import GithubClient
from aiohttp_session import get_session, session_middleware
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from pystache import render

from . import log, conf, Repo, pretty_json, get_restart_url
from .build import gh_api, get_restart_ctx, get_hook_ctx, build


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
    url('/logs/{path:.*}', logs)
    url('/hook', hook, method='POST')

    prefix = '{prefix:(%s)}' % '|'.join(i.name for i in Repo)
    url(r'/%s' % prefix, repo)
    url(r'/%s/restart/{typ:(pr|br)}/{ref:.+}' % prefix, restart)

    # TODO: keep it for a while
    url('/push/{p:.*}', lambda r: web.HTTPFound('/logs/' + r.match_info['p']))
    return app


async def auth_middleware(app, handler):
    """ Login via Github """
    def gh_client(**kw):
        return GithubClient(conf['github_id'], conf['github_secret'], **kw)

    async def callback(request):
        session = await get_session(request)
        if session.get('github_state') != request.GET.get('state'):
            return web.HTTPBadRequest()
        gh = gh_client()
        code = request.GET.get('code')
        if not code:
            return web.HTTPBadRequest()

        token, _ = await gh.get_access_token(code)
        gh = gh_client(access_token=token)
        req = await gh.request('GET', 'user')
        user = await req.json()
        req.close()
        users = []
        for org in conf['github_orgs']:
            _, resp = await gh_api('orgs/%s/members' % org)
            users.extend(u['login'] for u in resp)
        if user.get('login') in users:
            session['login'] = user.get('login')
            session.pop('github_state', None)
            location = session.pop('location')
            return web.HTTPFound(location)
        return web.HTTPForbidden()

    async def check_auth(request):
        session = await get_session(request)
        login = session.get('login')
        if login:
            request['login'] = login
        else:
            gh = gh_client()
            state = str(uuid.uuid4())
            url = gh.get_authorize_url(scope='', state=state)
            session['github_state'] = state
            session['location'] = request.path
            return web.HTTPFound(url)
        return await handler(request)

    async def inner(request):
        if request.path == (conf['url_prefix'] + conf['github_callback']):
            return await callback(request)
        elif request.path == (conf['url_prefix'] + '/hook'):
            return await handler(request)
        else:
            return await check_auth(request)

    return inner


async def logs(request):
    path = '/.logs/%s' % request.match_info['path']
    return web.HTTPOk(
        headers=[('X-Accel-Redirect', path)],
        content_type='text/html' if path.endswith('.htm') else 'text/plain',
    )


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
    log.info('%s\n\n%s', pretty_json(headers), pretty_json(body))
    ctx = get_hook_ctx(headers, body, clean=True)
    if ctx:
        os.makedirs(ctx['logpath'], exist_ok=True)
        with open(ctx['path'] + '/request.json', 'w') as f:
            f.write(pretty_json([headers, body]))
        # async with async_open(ctx['path'] + '/request.json', 'w') as f:
        #     await f.write(pretty_json([headers, body]))

        request.app.loop.create_task(build(ctx))
    return web.json_response(ctx)


async def restart(request):
    prefix = request.match_info['prefix']
    try:
        Repo[prefix]
    except KeyError:
        return web.HTTPNotFound()

    typ = request.match_info['typ']
    ref = request.match_info['ref']
    sha = request.GET.get('sha')
    clean = request.GET.get('clean', False)

    if typ == 'br':
        ref = 'refs/heads/' + ref

    ctx = await get_restart_ctx(prefix, ref, sha, typ == 'pr', clean=clean)
    if not ctx:
        return web.HTTPBadRequest()

    request.app.loop.create_task(build(ctx))
    return web.HTTPFound(ctx['logurl'])


async def index(request):
    ctx = {'repo': [{'prefix': i.name, 'name': i.value} for i in Repo]}
    return render_tpl(index_tpl, ctx)
index_tpl = '''
<ul>
{{#repo}}
    <li><a href="{{prefix}}">{{name}}</a></li>
{{/repo}}
</ul>
'''


async def repo(request):
    prefix = request.match_info['prefix']
    try:
        repo_name = Repo[prefix]
    except KeyError:
        return web.HTTPNotFound()

    def info(ctx, pr=False):
        if pr:
            name = ctx['number']
            subdomain = '%spr-%s' % (prefix, name)
            gh_url = ctx['html_url']
        else:
            name = ctx['name']
            name_cleaned = re.sub('[^a-z0-9]', '', name)
            subdomain = '%s-%s' % (prefix, name_cleaned)
            gh_url = 'https://github.com/%s/tree/%s' % (repo_name, name)
        return {
            'name': name,
            'url': 'https://%s.%s' % (subdomain, conf['domain']),
            'gh_url': gh_url,
            'restart_url': get_restart_url(prefix, name, pr),
        }

    resp, body = await gh_api('repos/%s/pulls' % repo_name)
    pulls = [info(i, True) for i in sorted(body, key=lambda i: i['number'])]

    resp, body = await gh_api('repos/%s/branches' % repo_name)
    branches = [info(i) for i in sorted(body, key=lambda i: i['name'])]

    ctx = {'pulls': pulls, 'branches': branches}
    return render_tpl(repo_tpl, ctx)
repo_tpl = '''
<b>Pull requests</b>
<ul>
{{#pulls}}
    <li>
        <a href="{{url}}">{{name}}</a>
        <a href="{{gh_url}}" title="Github">[gh]</a>
        <a href="{{restart_url}}" style="color:red" title="Restart">[r]</a>
    </li>
{{/pulls}}
</ul>

<b>Branches</b>
<ul>
{{#branches}}
    <li>
        <a href="{{url}}">{{name}}</a>
        <a href="{{gh_url}}" title="Github">[gh]</a>
        <a href="{{restart_url}}" style="color:red" title="Restart">[r]</a>
    </li>
{{/branches}}
</ul>
'''


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
    resp = web.Response(text=render(tpl, ctx))
    resp.content_type = content_type
    resp.set_status(status)
    return resp


def get_signature(body):
    sha1 = hmac.new(conf['secret'].encode(), body, hashlib.sha1).hexdigest()
    return 'sha1=' + sha1


app = get_app()
if __name__ == '__main__':
    web.run_app(app, port=os.environ.get('PORT', 8080))
