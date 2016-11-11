#!/usr/bin/env python3
import asyncio
import base64
import datetime as dt
import hashlib
import hmac
import json
import os
import re
from pathlib import Path

from aiofiles import open
from aiohttp import web, ClientSession

root = Path(__file__).resolve().parent
domain = 'test.superdesk.org'

async def get_config():
    async with open('config.json', 'r') as f:
        conf = await f.read()
    return json.loads(conf)


def pretty_json(obj):
    return json.dumps(obj, indent=2, sort_keys=True)


async def sh(cmd, ctx, *, logfile=None):
    ctx = ctx or {}
    cmd = 'set -ex; cd %s; %s' % (root, cmd.format(**ctx))
    logfile = logfile or ctx['logfile']
    if logfile:
        cmd = '(%s) >> %s 2>&1' % (cmd, ctx['logpath'] + logfile)
    print(cmd)
    proc = await asyncio.create_subprocess_shell(cmd)
    code = await proc.wait()
    print(code, cmd)
    return code


def get_ctx(headers, body):
    event = headers.get('X-Github-Event')
    if event == 'pull_request':
        if body['action'] not in ('opened', 'reopened', 'synchronize'):
            return {}
        sha = body['pull_request']['head']['sha']
        name = body['number']
        prefix = 'pr'
        env = 'repo_pr=%s repo_sha=%s' % (body['number'], sha)
    elif event == 'push':
        sha = body['after']
        branch = body['ref'].replace('refs/heads/', '')
        name = re.sub('[^a-z0-9]', '', branch)
        prefix = ''
        env = 'repo_sha=%s repo_branch=%s' % (sha, branch)
    else:
        return {}

    repo = body['repository']['full_name']
    if repo.startswith('naspeh-sf'):
        # For testing purpose
        repo = repo.replace('naspeh-sf', 'superdesk')

    if repo == 'superdesk/superdesk':
        endpoint = 'superdesk-dev/master'
        prefix = 'sd' + prefix
        checks = {'name': 'sd_checks'}
    elif repo == 'superdesk/superdesk-core':
        endpoint = 'superdesk-dev/core'
        prefix = 'sds' + prefix
        checks = {'name': 'sds_checks', 'env': 'frontend='}
    else:
        print('Repository %r is not supported', repo)
        return {}

    name = '%s-%s' % (prefix, name)
    uniq = (name, sha[:10])
    name_uniq = '%s-%s' % uniq
    path = 'push/%s/%s' % uniq
    env += ' repo_remote=%s' % body['repository']['clone_url']
    ctx = {
        'sha': sha,
        'name': name,
        'name_uniq': name_uniq,
        'path': path,
        'endpoint': endpoint,
        'checks': checks,
        'logpath': (
            '{path}/{time:%Y%m%d-%H%M%S}-'
            .format(path=path, time=dt.datetime.now())
        ),
        'logfile': 'push.log',
        'env': env,
        'statuses_url': body['repository']['statuses_url'].format(sha=sha)
    }
    ctx['logurl'] = 'https://%s/%s' % (domain, ctx['logpath'])
    return ctx


async def post_status(ctx, state=None, extend=None, code=None):
    assert state is not None or code is not None
    if code is not None:
        state = 'success' if code == 0 else 'failure'

    data = {
        'state': state,
        'target_url': ctx['logurl'] + ctx['logfile'],
        'description': 'Superdesk Deploy',
        'context': 'naspeh-sf/deploy/push'
    }
    if extend:
        data.update(extend)
    conf = await get_config()
    b64auth = base64.b64encode(conf['github_auth'].encode()).decode()
    headers = {'Authorization': 'Basic %s' % b64auth}
    async with ClientSession(headers=headers) as s:
        async with s.post(ctx['statuses_url'], data=json.dumps(data)) as resp:
            print('Posted status: %s' % resp.status)
            print(pretty_json(await resp.json()))
            return resp


async def sd_checks(ctx):
    return await sh('''
    lxc-start -n {name_uniq};
    ./fire lxc-wait {name_uniq};
    ./fire r --lxc-name={name_uniq} --env="{env}" -e {endpoint} -a do_checks;
    ''', ctx)


async def sds_checks(ctx):
    targets = ['flake8', 'nose', 'behave']
    cmd = '''
    lxc={name_uniq}-{t};
    name=$lxc base={name_uniq} bin/lxc-copy.sh;
    ./fire r --lxc-name=$lxc --env="{env}" -e {endpoint} -a "{t}=1 do_checks"
    '''

    async def run(target):
        logfile = 'check-%s.log' % target
        status = {
            'target_url': ctx['logurl'] + logfile,
            'context': 'naspeh-sf/deploy/check-%s' % target
        }
        await post_status(ctx, 'pending', extend=status)
        code = await sh(
            cmd.format(t=target, **ctx),
            ctx, logfile=logfile
        )
        await post_status(ctx, code=code, extend=status)
        print('Finished %r with %s' % (target, code))
        return code

    proces = [run(t) for t in targets]
    failed = False
    for f in asyncio.as_completed(proces):
        failed = await f or failed
    return failed and 1 or 0


async def checks(ctx):
    async def clean(code):
        await post_status(ctx, code=code)
        await sh('./fire lxc-clean "^{name_uniq}"', ctx)

    name = ctx['checks']['name']
    env = ctx['checks'].get('env', '')

    code = await sh('''
    name={name_uniq} bin/lxc-copy.sh;
    ./fire lxc-wait {name_uniq};
    ./fire i --lxc-name={name_uniq} --env="{env}" -e {endpoint};
    lxc-stop -n {name_uniq};
    ''', dict(ctx, env='%s %s' % (env, ctx['env'])))

    if code:
        await clean(code)
        return

    code = await globals()[name](ctx)
    await clean(code)
    return code


async def pubweb(ctx):
    logfile = 'web.log'
    status = {
        'target_url': ctx['logurl'] + logfile,
        'context': 'naspeh-sf/deploy/web'
    }
    await post_status(ctx, 'pending', extend=status)
    code = await sh('''
    clean={clean} name={name} bin/lxc-copy.sh;
    ./fire i --lxc-name={name} --env="{env}" -e {endpoint} --prepopulate;
    name={name} . superdesk-dev/nginx.tpl > /etc/nginx/instances/{name};
    nginx -s reload || true
    ''', ctx, logfile=logfile)

    if code == 0:
        status['target_url'] = 'http://%s.%s' % (ctx['name'], domain)
    await post_status(ctx, code=code, extend=status)
    return code


async def gh_push(req, clean=False):
    ctx = get_ctx(req['headers'], req['json'])
    ctx.update(clean=clean or '')
    print(pretty_json(ctx))

    os.makedirs(ctx['path'], exist_ok=True)
    async with open(ctx['path'] + '/request.json', mode='w') as f:
        await f.write(pretty_json(req))

    resp = await post_status(ctx, 'pending')
    if resp.status != 201:
        return

    proces = [t(ctx) for t in (pubweb, checks)]
    failed = 0
    for f in asyncio.as_completed(proces):
        failed = await f or failed

    return failed


async def hook(request):
    conf = await get_config()
    body = await request.read()
    sha1 = hmac.new(conf['secret'].encode(), body, hashlib.sha1).hexdigest()
    is_gh = hmac.compare_digest(
        'sha1=' + sha1,
        request.headers.get('X-Hub-Signature')
    )
    if not is_gh:
        return web.json_response({'error': 'Wrong signature'})

    body = await request.json()
    headers = dict(request.headers.items())
    print(pretty_json(headers))
    print(pretty_json(body))
    ctx = get_ctx(headers, body)
    if ctx:
        request.app.loop.create_task(
            gh_push({'headers': headers, 'json': body})
        )
    return web.json_response('OK')


def get_app():
    app = web.Application()
    app.router.add_post('/', hook)
    return app

if __name__ == '__main__':
    web.run_app(get_app())
