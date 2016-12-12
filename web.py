#!/usr/bin/env python3
import asyncio
import datetime as dt
import hashlib
import hmac
import json
import os
import re
import uuid
import warnings
from asyncio.subprocess import PIPE

# from aiofiles import open as async_open
from aiohttp import web, ClientSession
from aioauth_client import GithubClient
from aiohttp_session import get_session, session_middleware
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from pystache import render

from common import root, log, conf, repos, gh_auth, pretty_json

repos_reverse = {v: k for k, v in repos.items()}


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

    prefix = '{prefix:(%s)}' % '|'.join(repos)
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
    if prefix not in repos:
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
    ctx = {'repo': [{'prefix': k, 'name': v} for k, v in repos.items()]}
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
    if prefix not in repos:
        return web.HTTPNotFound()

    repo_name = repos[prefix]

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


async def sh(cmd, ctx, *, logfile=None):
    cmd = 'set -ex; cd %s; %s' % (root, cmd.format(**ctx))
    logfile = logfile or ctx['logfile']
    if logfile:
        cmd = (
            '(time ({cmd})) 2>&1'
            '  | tee -a {path}'
            '  | aha -w --black >> {path}.htm;'
            '[ "0" = "${{PIPESTATUS[0]}}" ] && true'
            .format(cmd=cmd, path=ctx['logpath'] + logfile)
        )
    log.info(cmd)
    proc = await asyncio.create_subprocess_shell(cmd, executable='/bin/bash')
    code = await proc.wait()
    log.info('code=%s: %s', code, cmd)
    return code


async def get_restart_ctx(short_name, ref, sha=None, pr=False, **extend):
        name = repos[short_name]
        if not sha and pr:
            resp, body = await gh_api('repos/%s/pulls/%s' % (name, ref))
            sha = body['head']['sha']
        elif not sha:
            resp, body = await gh_api('repos/%s/branches/%s' % (name, ref))
            sha = body['commit']['sha']
        return get_ctx(name, ref, sha, pr, **extend)


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


def get_ctx(repo_name, ref, sha, pr=False, **extend):
    if repo_name.startswith('naspeh-sf'):
        # For testing purpose
        repo_name = repo_name.replace('naspeh-sf', 'superdesk')

    if repo_name not in repos.values():
        log.warn('Repository %r is not supported', repo_name)
        return {}

    if repo_name == 'superdesk/superdesk':
        endpoint = 'superdesk-dev/master'
        checks = {
            'targets': ['flake8', 'npmtest'],
            'env': 'lxc_data=data-sd--tests'
        }
        env = ''
    elif repo_name == 'superdesk/superdesk-core':
        endpoint = 'superdesk-dev/core'
        checks = {
            'targets': ['docs', 'flake8', 'nose', 'behave'],
            'env': 'frontend='
        }
    elif repo_name == 'superdesk/superdesk-client-core':
        endpoint = 'superdesk-dev/client-core'
        checks = {
            'targets': ['e2e', 'npmtest', 'docs'],
            'env': 'lxc_data=data-sd--tests'
        }

    prefix = repos_reverse[repo_name]
    if pr:
        env = ' repo_pr=%s repo_sha=%s' % (ref, sha)
        name = ref
        prefix += 'pr'
    elif ref.startswith('refs/heads/'):
        ref = ref.replace('refs/heads/', '')
        prefix += ''
        name = re.sub('[^a-z0-9]', '', ref)
        env = 'repo_sha=%s repo_branch=%s' % (sha, ref)

        rel = re.match('^v?(1\.[01234])(\..*)?', ref)
        if rel:
            env += ' repo_main_branch=1.0 repo_pair_branch=%s' % rel.group()
    else:
        log.info('Skip repo_name=%s ref=%s', repo_name, ref)
        return {}

    clone_url = 'https://github.com/%s.git' % repo_name
    name = '%s-%s' % (prefix, name)
    uniq = (name, sha[:10])
    name_uniq = '%s-%s' % uniq
    host = '%s.%s' % (name, conf['domain'])
    path = 'logs/%s/%s' % uniq
    env += ' repo_remote=%s host=%s' % (clone_url, host)
    ctx = {
        'sha': sha,
        'repo_name': repo_name,
        'prefix': prefix,
        'ref': ref,
        'name': name,
        'name_uniq': name_uniq,
        'name_uniq_orig': name_uniq,
        'host': '%s.%s' % (name, conf['domain']),
        'path': path,
        'endpoint': endpoint,
        'checks': checks,
        'logpath': (
            '{path}/{time:%Y%m%d-%H%M%S}/'
            .format(path=path, time=dt.datetime.now())
        ),
        'logfile': 'build.log',
        'env': env,
        'lxc_base': conf['lxc_base'],
        'e2e_chunks': conf['e2e_chunks'],
        'no_statuses': conf['no_statuses'],
        'statuses_url': 'repos/%s/statuses/%s' % (repo_name, sha),
    }
    ctx.update(**extend)
    ctx.update(
        logurl=conf['logurl'] + ctx['logpath'],
        clean=ctx.get('clean') and '--clean' or ''
    )
    os.makedirs(ctx['logpath'], exist_ok=True)
    log.info(pretty_json(ctx))
    return ctx


async def gh_api(url, data=None):
    if not url.startswith('https://'):
        url = 'https://api.github.com/' + url

    async with ClientSession(headers=gh_auth()) as s:
        if data is None:
            method = 'GET'
        else:
            method = 'POST'
            data = json.dumps(data)
        async with s.request(method, url, data=data) as resp:
            return resp, await resp.json()


async def post_status(ctx, state=None, extend=None, code=None, save_id=False):
    assert state is not None or code is not None
    if code is not None:
        state = 'success' if code == 0 else 'failure'

    data = {
        'state': state,
        'target_url': ctx['logurl'],
        'description': '',
        'context': conf['status_prefix'] + 'build'
    }
    if extend:
        data.update(extend)

    target_url = data['target_url']
    if target_url.endswith('.log') and state != 'pending':
        data['target_url'] = target_url + '.htm'

    if not ctx['no_statuses'] and not save_id:
        url = 'repos/{repo_name}/commits/{sha}/status'.format(**ctx)
        resp, body = await gh_api(url)
        last_status = [
            s for s in body['statuses']
            if s['context'] == (conf['status_prefix'] + 'build')
        ]
        if not last_status or last_status[0]['id'] != ctx.get('build_id'):
            ctx['no_statuses'] = True
            ctx['build_restarted'] = True
            ctx['build_status'] = 'build\'s been probably restarted'

    if ctx['no_statuses']:
        data['!'] = 'wasn\'t sent: %s' % ctx.get('build_status', 'skipped')
        body = pretty_json(data)
        log.info('Local status:\n%s', body)
    else:
        resp, body = await gh_api(ctx['statuses_url'], data=data)
        if save_id:
            ctx['build_id'] = body.get('id')
        body = pretty_json(body)
        log.info('Posted status: %s\n%s', resp.status, body)
        if resp.status != 201:
            log.warn(pretty_json(data))
    target = data['context'].replace(conf['status_prefix'], '')
    path = '{path}{target}-{state}.json'.format(
        path=ctx['logpath'],
        target=target,
        state=state
    )
    with open(path, 'w') as f:
        f.write(body)
    # async with async_open(path, 'w') as f:
    #     await f.write(body)


def chunked_specs(sizes, n, names=None):
    names = sorted((k for k, v in sizes), reverse=True)
    sizes = {k: int(v) for k, v in sizes}

    def chunk(names, n):
        if n == 1:
            size = sum(v for k, v in sizes.items() if k in names)
            log.info('size=%s; files=%s', size, names)
            return names

        chunk, size = [], 0
        chunksize = sum(v for k, v in sizes.items() if k in names) / n
        while size < chunksize:
            new_size = size + int(sizes[names[-1]])
            if new_size > chunksize:
                break
            size = new_size
            chunk.append(names.pop())
        log.info('size=%s; files=%s', size, chunk)
        return chunk

    for i in range(n):
        res = chunk(names, n - i)
        if res:
            yield res


async def check_e2e(ctx):
    ctx.update(name_uniq='%s-e2e' % ctx['name_uniq'])
    code = await sh('''
    ./fire lxc-copy --clean -sb {name_uniq_orig} {name_uniq};
    ./fire r -e {endpoint} --lxc-name {name_uniq} --env="{env}" -a _checks_init
    ''', ctx)
    if code != 0:
        return code

    pattern = '*' * 30
    cmd = '''
    cd {r} &&
    ./fire r -e {endpoint} --lxc-name={name_uniq} -a 'pattern="{p}" do_specs'
    '''.format(r=root, p=pattern, **ctx)
    proc = await asyncio.create_subprocess_shell(cmd, stdout=PIPE, stderr=PIPE)
    out, err = await proc.communicate()
    if proc.returncode != 0:
        log.error('ERROR: %s', err)
        return 1
    specs = out.decode().rsplit(pattern, 1)[-1]
    specs = [i.split() for i in specs.split('\n') if i]
    targets = chunked_specs(specs, ctx['e2e_chunks'])
    targets = [
        {
            'target': 'e2e--part%s' % num,
            'parent': 'e2e',
            'env': 'specs=%s' % ','.join(t)
        } for num, t in enumerate(targets, 1)
    ]
    code = await sh('lxc-stop -n {name_uniq}', ctx)
    if code != 0:
        return code
    code = await run_targets(ctx, targets)
    return code


async def run_target(ctx, target):
    cmd = '''
    lxc={name_uniq_orig}-{t};
    ./fire lxc-copy --clean -sb {name_uniq} $lxc
    ./fire r --lxc-name=$lxc --env="{env}" -e {endpoint} -a "{p}=1 do_checks"
    '''

    ctx = dict(ctx)
    if isinstance(target, dict):
        parent = target['parent']
        env = target['env']
        target = target['target']
        ctx['no_statuses'] = True
    else:
        parent, env = target, ''

    if target == 'e2e' and ctx['e2e_chunks'] == 0:
        return 0

    env = ' '.join(i for i in (env, ctx['env']) if i)
    logfile = 'check-%s.log' % target
    status = {
        'target_url': ctx['logurl'] + logfile,
        'context': conf['status_prefix'] + 'check-%s' % target
    }
    await post_status(ctx, 'pending', extend=status)
    if target == 'e2e' and ctx['e2e_chunks'] > 1:
        status['target_url'] = ctx['logurl']
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


async def www(ctx):
    logfile = 'www.log'
    status = {
        'target_url': ctx['logurl'] + logfile,
        'context': conf['status_prefix'] + 'www',
    }
    await post_status(ctx, 'pending', extend=status)

    code = await sh('''
    lxc={name_uniq}-www;
    env="{env} lxc_data=data-sd db_name={name}";
    ./fire lxc-copy --clean -sb {name_uniq} $lxc;
    ./fire r --lxc-name=$lxc --env="$env" -e {endpoint} -a "do_www";
    ./fire lxc-copy --no-snapshot -rcs -b $lxc {name};
    ./fire nginx || true
    ''', ctx, logfile=logfile)

    if code == 0:
        status['target_url'] = 'https://%s.%s' % (ctx['name'], conf['domain'])
    await post_status(ctx, code=code, extend=status)
    return code


async def post_restart_status(ctx, **kw):
    return await post_status(ctx, extend={
        'target_url': get_restart_url(
            repos_reverse[ctx['repo_name']],
            ctx['ref'],
            ctx['prefix'].endswith('pr')
        ),
        'context': conf['status_prefix'] + '!restart',
        'description': 'Click "Details" to restart the build',
    }, **kw)


async def build(ctx):
    async def clean_statuses(code=None):
        # Clean previous statuses
        state = 'pending'
        complete = code is not None
        if complete:
            state = 'success' if code == 0 else 'failure'
        statuses = [conf['status_prefix'] + s for s in ('build', '!restart')]
        url = 'repos/{repo_name}/commits/{sha}/status'.format(**ctx)
        resp, body = await gh_api(url)
        for s in body['statuses']:
            c = s['context']
            if not c.startswith(conf['status_prefix']) or c in statuses:
                continue
            statuses.append(c)
            if complete and s['state'] != 'pending':
                continue
            log.info('Previous status: %s', pretty_json(s))
            status = {
                'target_url': ctx['logurl'],
                'context': c,
                'description': (
                    'Rewritten: the status is missing in new build'
                    if complete else
                    'Restarted'
                )
            }
            await post_status(ctx, state, status)

    async def clean(code):
        await post_restart_status(ctx, code=code)
        await post_status(ctx, code=code, save_id=True)
        await clean_statuses(code)
        if not ctx.get('build_restarted'):
            await sh('./fire lxc-clean "^{name_uniq}-";', ctx)

    if not ctx:
        return 1

    await post_status(ctx, 'pending', save_id=True)
    await post_restart_status(ctx, state='pending')
    await clean_statuses()
    code = await sh('''
    (lxc-ls -1\
        | grep "^{name}-"\
        | grep -v "^{name_uniq}$"\
        | sort -r\
        | xargs -r ./fire lxc-rm) || true;
    [ -z "{clean}" ] && [ "$(lxc-info -n {name_uniq} -sH)" = 'STOPPED' ] || (
        ./fire lxc-copy --cpus={cpus} -sb {lxc_base} --clean {name_uniq};
        time ./fire i --lxc-name={name_uniq} --env="{env}" -e {endpoint};
        time lxc-stop -n {name_uniq};
    )
    # sed -i '/lxc.cgroup.cpuset.cpus/,$d' /var/lib/lxc/{name_uniq}/config;
    ''', dict(ctx, cpus=conf['use_cpus']))

    if code:
        await clean(code)
        return code

    proces = [t(ctx) for t in (www, checks)]
    code = await wait_for(proces)
    await clean(code)


def get_restart_url(prefix, ref, pr=False):
    return (
        'https://{domain}{base_url}/{prefix}/restart/{typ}/{ref}'
        .format(
            domain=conf['domain'],
            base_url=conf['url_prefix'],
            prefix=prefix,
            typ='pr' if pr else 'br',
            ref=ref
        )
    )


def get_signature(body):
    sha1 = hmac.new(conf['secret'].encode(), body, hashlib.sha1).hexdigest()
    return 'sha1=' + sha1


app = get_app()
if __name__ == '__main__':
    web.run_app(app, port=os.environ.get('PORT', 8080))
