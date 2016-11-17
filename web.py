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

from aiofiles import open as async_open
from aiohttp import web, ClientSession

root = Path(__file__).resolve().parent
conf = None


def pretty_json(obj):
    return json.dumps(obj, indent=2, sort_keys=True)


async def sh(cmd, ctx, *, logfile=None):
    cmd = 'set -ex; cd %s; %s' % (root, cmd.format(**ctx))
    logfile = logfile or ctx['logfile']
    if logfile:
        cmd = (
            '({cmd}) >> {path} 2>&1;'
            'code=$?;'
            'cat {path} | aha -w --black > {path}.htm;'
            'exit $code'
            .format(cmd=cmd, path=ctx['logpath'] + logfile)
        )
    print(cmd)
    proc = await asyncio.create_subprocess_shell(cmd)
    code = await proc.wait()
    print(code, cmd)
    return code


def get_ctx(headers, body, **extend):
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

    # mean it has been delated
    if sha == '0000000000000000000000000000000000000000':
        return {}

    repo = body['repository']['full_name']
    if repo.startswith('naspeh-sf'):
        # For testing purpose
        repo = repo.replace('naspeh-sf', 'superdesk')

    if repo == 'superdesk/superdesk':
        endpoint = 'superdesk-dev/master'
        prefix = 'sd' + prefix
        checks = {'targets': ['flake8', 'npmtest']}
    elif repo == 'superdesk/superdesk-core':
        endpoint = 'superdesk-dev/core'
        prefix = 'sds' + prefix
        checks = {
            'targets': ['flake8', 'nose', 'behave'],
            'env': 'frontend='
        }
    elif repo == 'superdesk/superdesk-client-core':
        endpoint = 'superdesk-dev/client-core'
        prefix = 'sdc' + prefix
        checks = {'targets': ['e2e', 'npmtest', 'docs']}
    else:
        print('Repository %r is not supported', repo)
        return {}

    name = '%s-%s' % (prefix, name)
    uniq = (name, sha[:10])
    name_uniq = '%s-%s' % uniq
    host = '%s.%s' % (name, conf['domain'])
    path = 'push/%s/%s' % uniq
    env += ' repo_remote=%s host=%s' % (body['repository']['clone_url'], host)
    ctx = {
        'sha': sha,
        'name': name,
        'name_uniq': name_uniq,
        'host': '%s.%s' % (name, conf['domain']),
        'path': path,
        'sdbase': conf['sdbase'],
        'endpoint': endpoint,
        'checks': checks,
        'logpath': (
            '{path}/{time:%Y%m%d-%H%M%S}/'
            .format(path=path, time=dt.datetime.now())
        ),
        'logfile': 'build.log',
        'env': env,
        'statuses_url': body['repository']['statuses_url'].format(sha=sha),
        'install': True
    }
    ctx.update(**extend)
    ctx.update(
        clean=ctx.get('clean') and '--clean' or '',
        clean_web=ctx.get('clean_web') and '--clean-web' or '',
        logurl=conf['logurl'] + ctx['logpath']
    )
    os.makedirs(ctx['logpath'], exist_ok=True)
    print(pretty_json(ctx))
    return ctx


async def post_status(ctx, state=None, extend=None, code=None):
    assert state is not None or code is not None
    if code is not None:
        state = 'success' if code == 0 else 'failure'

    logfile = ctx['logfile']
    if state != 'pending':
        logfile += '.htm'

    data = {
        'state': state,
        'target_url': ctx['logurl'] + logfile,
        'description': 'Superdesk Deploy',
        'context': 'naspeh-sf/deploy/build'
    }
    if extend:
        data.update(extend)
    b64auth = base64.b64encode(conf['github_auth'].encode()).decode()
    headers = {'Authorization': 'Basic %s' % b64auth}
    async with ClientSession(headers=headers) as s:
        async with s.post(ctx['statuses_url'], data=json.dumps(data)) as resp:
            body = pretty_json(await resp.json())
            print('Posted status: %s' % resp.status)
            print(body)
            if resp.status != 201:
                print(pretty_json(data))
            path = '{path}{target}-{state}.json'.format(
                path=ctx['logpath'],
                target=data['context'].rsplit('/', 1)[1],
                state=state
            )
            async with async_open(path, mode='w') as f:
                await f.write(body)
            return resp


async def checks(ctx):
    async def clean(code):
        await post_status(ctx, code=code)
        await sh(
            './fire lxc-clean "^{name_uniq}-";'
            '[ -z "{clean}" ] || ./fire lxc-rm {name_uniq}',
            ctx
        )

    targets = ctx['checks']['targets']
    env = ctx['checks'].get('env', '')

    if ctx['install']:
        code = await sh('''
        ./fire lxc-copy -s -b {sdbase} {clean} {name_uniq}
        ./fire i --lxc-name={name_uniq} --env="{env}" -e {endpoint};
        lxc-stop -n {name_uniq};
        ''', dict(ctx, env='%s %s' % (env, ctx['env'])))

        if code:
            await clean(code)
            return

    cmd = '''
    lxc={name_uniq}-{t};
    ./fire lxc-copy -s -b {name_uniq} $lxc
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
    code = 0
    for f in asyncio.as_completed(proces):
        code = await f or 1

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
    ./fire lxc-copy -s -b {sdbase} {clean_web} {name}
    ./fire i --lxc-name={name} --env="{env}" -e {endpoint} --prepopulate;
    name={name} host={host} \
        . superdesk-dev/nginx.tpl > /etc/nginx/instances/{name};
    nginx -s reload || true
    ''', ctx, logfile=logfile)

    if code == 0:
        status['target_url'] = 'http://%s.%s' % (ctx['name'], conf['domain'])
    await post_status(ctx, code=code, extend=status)
    return code


async def build(ctx):
    await post_status(ctx, 'pending')
    proces = [t(ctx) for t in (pubweb, checks)]
    failed = 0
    for f in asyncio.as_completed(proces):
        failed = await f or failed
    return failed


def get_signature(body):
    sha1 = hmac.new(conf['secret'].encode(), body, hashlib.sha1).hexdigest()
    return 'sha1=' + sha1


async def hook(request):
    body = await request.read()
    check_signature = hmac.compare_digest(
        get_signature(body),
        request.headers.get('X-Hub-Signature', '')
    )
    if not check_signature:
        return web.Response(status=400)

    body = await request.json()
    headers = dict(request.headers.items())
    del headers['X-Hub-Signature']
    print(pretty_json(headers))
    print(pretty_json(body))
    ctx = get_ctx(headers, body, clean=True)
    if ctx:
        os.makedirs(ctx['logpath'], exist_ok=True)
        async with async_open(ctx['path'] + '/request.json', mode='w') as f:
            await f.write(pretty_json([headers, body]))

        request.app.loop.create_task(build(ctx))
    return web.json_response('OK')


def init_conf():
    global conf
    with open('config.json', 'r') as f:
        conf = json.loads(f.read())

    defaults = [
        ('debug', False),
        ('sdbase', 'sdbase'),
        ('domain', 'localhost'),
        ('logurl', lambda c: 'http://%s/' % c['domain']),
    ]
    for key, value in defaults:
        if callable(value):
            value = value(conf)
        conf.setdefault(key, value)


def get_app():
    init_conf()
    app = web.Application()
    app.router.add_post('/', hook)
    app.router.add_static('/push', root / 'push', show_index=True)
    return app


if __name__ == '__main__':
    web.run_app(get_app(), port=os.environ.get('PORT', 8080))
