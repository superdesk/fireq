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


async def get_config():
    async with open('config.json', 'r') as f:
        conf = await f.read()
    return json.loads(conf)


def pretty_json(obj):
    return json.dumps(obj, indent=2, sort_keys=True)


def get_ctx(headers, body):
    event = headers.get('X-Github-Event')
    if event == 'pull_request':
        if body['action'] not in ('opened', 'reopened', 'synchronize'):
            return {}
        sha = body['pull_request']['head']['sha']
        name = 'sdpr--%s' % body['number']
        env = 'repo_pr=%s repo_sha=%s' % (body['number'], sha)
    elif event == 'push':
        sha = body['after']
        branch = body['ref'].replace('refs/heads/', '')
        name = re.sub('[^\w-]', '-', branch)
        name = 'sd--%s' % name
        env = 'repo_sha=%s repo_branch=%s' % (sha, branch)
    else:
        return {}

    env += ' repo_remote=%s' % body['repository']['clone_url']
    path = 'push/{name}/{sha}'.format(name=name, sha=sha)
    return {
        'sha': sha,
        'name': name,
        'path': path,
        'logfile': (
            '{path}/{time:%Y%m%d-%H%M%S}.log'
            .format(path=path, time=dt.datetime.now())
        ),
        'env': env,
        'statuses_url': body['repository']['statuses_url'].format(sha=sha)
    }


async def post_status(ctx, state, extend=None):
    data = {
        'state': state,
        'target_url': 'https://test.superdesk.org/%s' % ctx['logfile'],
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


async def sh(cmd, ctx, logfile=None, code=True):
    cmd = 'set -ex; cd %s; %s' % (root, cmd.format(**ctx))
    logfile = logfile or ctx.get('logfile')
    if logfile:
        cmd = '(%s) >> %s 2>&1' % (cmd, logfile)
    print(cmd)
    proc = await asyncio.create_subprocess_shell(cmd, stdout=None, stderr=None)
    if code:
        code = await proc.wait()
        print(code, cmd)
        return code
    return proc


async def gh_push(req, clean=True):
    ctx = get_ctx(req['headers'], req['json'])

    os.makedirs(ctx['path'], exist_ok=True)
    async with open(ctx['path'] + '/request.json', mode='w') as f:
        await f.write(pretty_json(req))

    ctx.update(**{
        'endpoint': 'superdesk-dev/master',
        'lxc_uniq': '{name}--{sha}'.format(**ctx),
        'clean': clean or '',
    })
    print(pretty_json(ctx))

    resp = await post_status(ctx, 'pending')
    if resp.status != 201:
        return

    code = await sh('''
    [ -n "{clean}" ] && (name={name} bin/lxc-copy.sh; sleep 10;)
    ./fire i --lxc-name={name} --env="{env}" -e {endpoint} --prepopulate;
    name={name} . superdesk-dev/nginx.tpl > /etc/nginx/sites-enabled/{name};
    nginx -s reload
    ''', ctx)

    await post_status(ctx, 'success' if code == 0 else 'failure', {
        'target_url': 'http://%s.test.superdesk.org' % ctx['name'],
        'context': 'naspeh-sf/deploy/web'
    })
    if code:
        await post_status(ctx, 'failure')
        return

    code = await sh('''
    name={lxc_uniq} from={name} bin/lxc-copy.sh;
    lxc-start -n {name};
    sleep 10;
    ./fire r --lxc-name={lxc_uniq} --env="{env}" -e {endpoint} -a do_tests;
    ''', ctx)

    await post_status(ctx, 'success' if code == 0 else 'failure')
    await sh('''
    lxc-stop -n {lxc_uniq} || true;
    lxc-destroy -n {lxc_uniq} || true;
    ''', ctx)


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
        # await gh_push({'headers': headers, 'json': body})

        req = {'headers': headers, 'json': body}
        os.makedirs(ctx['path'], exist_ok=True)
        async with open(ctx['path'] + '/request.json', mode='w') as f:
            await f.write(pretty_json(req))
        await sh('./fire gh-push -c {path}', ctx)
    return web.json_response('OK')


def get_app():
    app = web.Application()
    app.router.add_post('/', hook)
    return app

if __name__ == '__main__':
    web.run_app(get_app())
