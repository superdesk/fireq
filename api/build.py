import asyncio
import datetime as dt
import json
import os
import re
from asyncio.subprocess import PIPE

from aiohttp import ClientSession

from . import root, log, conf, Repo, utils


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


async def get_ctx(repo_name, ref, sha, **extend):
    if repo_name.startswith('naspeh-sf'):
        # For testing purpose
        repo_name = repo_name.replace('naspeh-sf', 'superdesk')

    try:
        prefix = Repo(repo_name).name
    except ValueError:
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

    if not sha:
        resp, body = await gh_api('repos/%s/git/refs/%s' % (repo_name, ref))
        if resp.status != 200:
            log.warn('Wrong ref: %s', ref)
            return {}
        if isinstance(body, list):
            sha = body[0]['object']['sha']
        else:
            sha = body['object']['sha']

    env = 'repo_ref=%s repo_sha=%s' % (ref, sha)
    if ref.startswith('pull/'):
        name = re.sub('[^0-9]', '', ref)
        prefix += 'pr'
        env += ' repo_pr=1'

    elif ref.startswith('heads/'):
        prefix += ''
        name = re.sub('^heads/', '', ref)
        name = re.sub('[^a-z0-9]', '', name)

        rel = re.match('^heads/v?(1\.[01234])(\..*)?', ref)
        if rel:
            env += ' repo_main_branch=1.0 repo_pair_branch=%s' % rel.group(1)
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
        'env': ' '.join(i for i in (env, extend.pop('env', None)) if i),
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
    log.info(utils.pretty_json(ctx))
    return ctx


async def gh_api(url, data=None):
    if not url.startswith('https://'):
        url = 'https://api.github.com/' + url

    async with ClientSession(headers=utils.gh_auth()) as s:
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
        body = utils.pretty_json(data)
        log.info('Local status:\n%s', body)
    else:
        resp, body = await gh_api(ctx['statuses_url'], data=data)
        if save_id:
            ctx['build_id'] = body.get('id')
        body = utils.pretty_json(body)
        log.info('Posted status: %s\n%s', resp.status, body)
        if resp.status != 201:
            log.warn(utils.pretty_json(data))
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
    ./fire r -e {endpoint} --lxc-name={name_uniq} --env="{env}" -a _checks_init
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

    logs = 'logs/{name}/logs'.format(**ctx)
    logsurl = conf['logurl'] + logs
    logs = '%s/%s' % (root, logs)

    code = await sh('''
    lxc={name_uniq}-www;
    env="{env} lxc_data=data-sd db_name={name} mails={logsurl}/mail";
    ./fire lxc-copy --clean -sb {name_uniq} $lxc;
    ./fire r --lxc-name=$lxc --env="$env" -e {endpoint} -a "do_www";
    ./fire lxc-copy --no-snapshot -rc -b $lxc {name};
    echo "lxc.mount.entry = {logs} var/log/superdesk none bind,create=dir" >>\
        /var/lib/lxc/{name}/config;
    mkdir -p {logs};
    lxc-start -n {name};
    ./fire nginx || true
    ''', dict(ctx, logs=logs, logsurl=logsurl), logfile=logfile)

    if code == 0:
        status['target_url'] = 'https://%s.%s' % (ctx['name'], conf['domain'])
    await post_status(ctx, code=code, extend=status)
    return code


async def post_restart_status(ctx, **kw):
    return await post_status(ctx, extend={
        'target_url': utils.get_restart_url(
            Repo(ctx['repo_name']).name,
            ctx['ref'],
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
            log.info('Previous status: %s', utils.pretty_json(s))
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
