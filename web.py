#!/usr/bin/env python3
import asyncio
import collections
import datetime as dt
import hashlib
import hmac
import json
import os
import re
import warnings
from asyncio.subprocess import PIPE

# from aiofiles import open as async_open
from aiohttp import web, ClientSession
from pystache import render

from common import root, log, conf, gh_auth, pretty_json

repos = collections.OrderedDict((
    ('sd', 'superdesk/superdesk'),
    ('sds', 'superdesk/superdesk-core'),
    ('sdc', 'superdesk/superdesk-client-core'),
))


def get_app():
    app = web.Application()
    init_loop(app.loop)
    r = app.router
    r.add_static('/push', root / 'push', show_index=True)
    r.add_get('/', index)
    r.add_post('/hook/', hook)

    prefix = '{prefix:(%s)}' % '|'.join(repos)
    r.add_get(r'/%s/restart/{typ:(pr|br)}/{ref:.+}' % prefix, restart)
    r.add_get(r'/%s/' % prefix, repo)
    return app


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
    log.info('%s\n\n%s', pretty_json(headers), pretty_json(body))
    ctx = get_hook_ctx(headers, body, clean=True)
    if ctx:
        request.app.loop.create_task(build(ctx))
    return web.json_response(ctx)


async def restart(request):
    prefix = request.match_info['prefix']
    log.info(prefix)
    if prefix not in repos:
        return web.HTTPNotFound()
    name = repos[prefix]
    typ = request.match_info['typ']
    ref = request.match_info['ref']
    sha = request.GET.get('sha')

    ctx = get_ctx(name, ref, sha, typ == 'pr')
    if not ctx:
        return web.HTTPBadRequest()

    request.app.loop.create_task(build(ctx))
    return web.HTTPFound(ctx['logurl'])


index_tpl = '''
<ul>
{{#repo}}
    <li><a href="{{prefix}}/">{{name}}</a></li>
{{/repo}}
</ul>
'''
async def index(request):
    ctx = {'repo': [{'prefix': k, 'name': v} for k, v in repos.items()]}
    return render_tpl(index_tpl, ctx)


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
async def repo(request):
    prefix = request.match_info['prefix']
    if prefix not in repos:
        return web.HTTPNotFound()

    name = repos[prefix]
    resp, body = await gh_api(name + '/pulls')
    pulls = []
    for i in sorted(body, key=lambda i: i['number']):
        pulls.append({
            'name': i['number'],
            'url': 'http://%spr-%s.%s' % (prefix, i['number'], conf['domain']),
            'gh_url': i['html_url'],
            'restart_url': (
                'restart/pr/%s?sha=%s'
                % (i['number'], i['head']['sha'])
            ),
        })

    resp, body = await gh_api(name + '/branches')
    branches = []
    for i in sorted(body, key=lambda i: i['name']):
        branches.append({
            'name': i['name'],
            'url': 'http://%s-%s.%s' % (prefix, i['name'], conf['domain']),
            'gh_url': 'https://github.com/%s/tree/%s' % (name, i['name']),
            'restart_url': (
                'restart/br/%s?sha=%s'
                % (i['name'], i['commit']['sha'])
            ),
        })

    ctx = {'pulls': pulls, 'branches': branches}
    return render_tpl(repo_tpl, ctx)


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


async def sh(cmd, ctx, *, logfile=None):
    cmd = 'set -ex; cd %s; %s' % (root, cmd.format(**ctx))
    logfile = logfile or ctx['logfile']
    if logfile:
        cmd = (
            '(time ({cmd})) 2>&1'
            '  | tee -a {path}'
            '  | aha -w --black >> {path}.htm;'
            'exit ${{PIPESTATUS[0]}}'
            .format(cmd=cmd, path=ctx['logpath'] + logfile)
        )
    log.info(cmd)
    proc = await asyncio.create_subprocess_shell(cmd, executable='/bin/bash')
    code = await proc.wait()
    log.info('code=%s: %s', code, cmd)
    return code


def get_hook_ctx(headers, body, **extend):
    event = headers.get('X-Github-Event')
    if event == 'pull_request':
        if body['action'] not in ('opened', 'reopened', 'synchronize'):
            return {}
        sha = body['pull_request']['head']['sha']
        ref = body['number']
        pr = True
    elif event == 'push':
        sha = body['after']
        ref = body['ref']
        pr = False
    else:
        return {}

    # mean it has been delated
    if sha == '0000000000000000000000000000000000000000':
        return {}

    repo_name = body['repository']['full_name']
    return get_ctx(repo_name, ref, sha, pr=pr, **extend)


def get_ctx(repo_name, ref, sha=None, pr=False, **extend):
    if repo_name.startswith('naspeh-sf'):
        # For testing purpose
        repo_name = repo_name.replace('naspeh-sf', 'superdesk')

    if repo_name not in repos.values():
        log.warn('Repository %r is not supported', repo_name)
        return {}

    if repo_name == 'superdesk/superdesk':
        endpoint = 'superdesk-dev/master'
        checks = {'targets': ['flake8', 'npmtest']}
    elif repo_name == 'superdesk/superdesk-core':
        endpoint = 'superdesk-dev/core'
        checks = {
            'targets': ['docs', 'flake8', 'nose', 'behave'],
            'env': 'frontend='
        }
    elif repo_name == 'superdesk/superdesk-client-core':
        endpoint = 'superdesk-dev/client-core'
        checks = {'targets': ['e2e', 'npmtest', 'docs']}

    prefix = list(repos.keys())[list(repos.values()).index(repo_name)]
    if pr:
        env = 'repo_pr=%s repo_sha=%s' % (ref, sha)
        name = ref
        prefix += 'pr'
    else:
        refs = (
            ('refs/heads/', ''),
            ('refs/tags/', 'tag'),
        )
        for b, p in refs:
            if not ref.startswith(b):
                continue
            ref = ref.replace(b, '')
            prefix += p
            break

        name = re.sub('[^a-z0-9]', '', ref)
        env = 'repo_sha=%s repo_branch=%s' % (sha, ref)

    clone_url = 'https://github.com/%s.git' % repo_name
    name = '%s-%s' % (prefix, name)
    uniq = (name, sha[:10])
    name_uniq = '%s-%s' % uniq
    host = '%s.%s' % (name, conf['domain'])
    path = 'push/%s/%s' % uniq
    env += ' repo_remote=%s host=%s' % (clone_url, host)
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
        'statuses_url': '%s/statuses/%s' % (repo_name, sha),
        'install': True
    }
    ctx.update(**extend)
    ctx.update(
        clean=ctx.get('clean') and '--clean' or '',
        clean_web=ctx.get('clean_web') and '--clean-web' or '',
        logurl=conf['logurl'] + ctx['logpath']
    )
    os.makedirs(ctx['logpath'], exist_ok=True)
    log.info(pretty_json(ctx))
    return ctx


async def gh_api(url, data=None):
    if not url.startswith('https://'):
        url = 'https://api.github.com/repos/' + url

    async with ClientSession(headers=gh_auth()) as s:
        if data is None:
            method = 'GET'
        else:
            method = 'POST'
            data = json.dumps(data)
        async with s.request(method, url, data=data) as resp:
            return resp, await resp.json()


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
    resp, body = await gh_api(ctx['statuses_url'], data=data)
    body = pretty_json(body)
    log.info('Posted status: %s\n%s', resp.status, body)
    if resp.status != 201:
        log.warn(pretty_json(data))
    path = '{path}{target}-{state}.json'.format(
        path=ctx['logpath'],
        target=data['context'].rsplit('/', 1)[1],
        state=state
    )
    with open(path, 'w') as f:
        f.write(body)
    # async with async_open(path, 'w') as f:
    #     await f.write(body)
    return resp


def chunked_specs(l, n):
    l = dict(i.split() for i in l.split('\n') if i)
    chunksize = sum(int(i) for i in l.values()) / n
    names = sorted(l)
    chunk, size = [], 0
    for name in names:
        size += int(l[name])
        chunk.append(name)
        if size > chunksize:
            yield chunk
            chunk, size = [], 0
    if chunk:
        yield chunk


async def check_e2e(ctx):
    ctx.update(name_e2e='%s-e2e' % ctx['name_uniq'])
    code = await sh('./fire lxc-copy -sb {name_uniq} {name_e2e}', ctx)
    if code != 0:
        return code

    pattern = '*' * 30
    cmd = '''
    cd {r} &&
    ./fire r -e {endpoint} --lxc-name={name_e2e} -a 'pattern="{p}" do_specs'
    '''.format(r=root, p=pattern, **ctx)
    proc = await asyncio.create_subprocess_shell(cmd, stdout=PIPE, stderr=PIPE)
    out, err = await proc.communicate()
    if proc.returncode != 0:
        log.error('ERROR: %s', err)
        return 1
    specs = out.decode().rsplit(pattern, 1)[-1]
    targets = chunked_specs(specs, conf['e2e_count'])
    targets = [
        {
            'target': 'e2e--part%s' % num,
            'parent': 'e2e',
            'env': 'specs=%s' % ','.join(t)
        } for num, t in enumerate(targets, 1)
    ]
    code = await run_targets(ctx, targets)
    return code


async def run_target(ctx, target):
    cmd = '''
    lxc={name_uniq}-{t};
    ./fire lxc-copy {clean} -s -b {name_uniq} $lxc
    ./fire r --lxc-name=$lxc --env="{env}" -e {endpoint} -a "{p}=1 do_checks"
    '''

    if isinstance(target, dict):
        parent = target['parent']
        env = target['env']
        target = target['target']
    else:
        parent, env = target, ''
    env = ' '.join(i for i in (env, ctx['env']) if i)

    logfile = 'check-%s.log' % target
    status = {
        'target_url': ctx['logurl'] + logfile,
        'context': 'naspeh-sf/deploy/check-%s' % target
    }
    await post_status(ctx, 'pending', extend=status)
    if target == 'e2e':
        code = await check_e2e(dict(ctx, logfile=logfile))
    else:
        c = dict(ctx, p=parent, t=target, env=env)
        code = await sh(cmd, c, logfile=logfile)
    await post_status(ctx, code=code, extend=status)
    log.info('Finished %r with %s', target, code)
    return code


async def wait_for(proces):
    failed = 0
    for f in asyncio.as_completed(proces):
        failed = await f or failed
    return failed


async def run_targets(ctx, targets):
    proces = [run_target(dict(ctx), t) for t in targets]
    return await wait_for(proces)


async def checks(ctx):
    targets = ctx['checks']['targets']
    env = ctx['checks'].get('env', '')
    env = ' '.join(i for i in (env, ctx['env']) if i)

    code = await run_targets(dict(ctx, env=env), targets)
    return code


async def pubweb(ctx):
    logfile = 'web.log'
    status = {
        'target_url': ctx['logurl'] + logfile,
        'context': 'naspeh-sf/deploy/web'
    }
    await post_status(ctx, 'pending', extend=status)

    code = await sh('''
    lxc={name_uniq}-web;
    env="{env} db_name={name}";
    ./fire lxc-copy {clean} -s -b {name_uniq} $lxc;
    ./fire r --lxc-name=$lxc --env="$env" -e {endpoint} -a "do_web";
    ./fire lxc-copy --no-snapshot -rcs -b $lxc {name};
    ./fire nginx || true
    ''', ctx, logfile=logfile)

    if code == 0:
        status['target_url'] = 'http://%s.%s' % (ctx['name'], conf['domain'])
    await post_status(ctx, code=code, extend=status)
    return code


async def build(ctx):
    async def clean(code):
        await post_status(ctx, code=code)
        await sh(
            './fire lxc-clean "^{name_uniq}-";'
            '[ -z "{clean}" ] || ./fire lxc-rm {name_uniq}',
            ctx
        )

    await post_status(ctx, 'pending')
    if ctx['install']:
        code = await sh('''
        time ./fire lxc-clean "^{name_uniq}-" || true;
        time ./fire lxc-copy -s -b {sdbase} {clean} {name_uniq};
        time ./fire i --lxc-name={name_uniq} --env="{env}" -e {endpoint};
        time lxc-stop -n {name_uniq};
        ''', ctx)

        if code:
            await clean(code)
            return code

    proces = [t(ctx) for t in (pubweb, checks)]
    code = await wait_for(proces)
    await clean(code)


def get_signature(body):
    sha1 = hmac.new(conf['secret'].encode(), body, hashlib.sha1).hexdigest()
    return 'sha1=' + sha1


app = get_app()
if __name__ == '__main__':
    web.run_app(app, port=os.environ.get('PORT', 8080))
