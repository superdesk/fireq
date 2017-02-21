import argparse
import datetime as dt
import json
import random
import re
import subprocess as sp
import time
import urllib.request
from concurrent import futures
from collections import namedtuple
from pathlib import Path

from pystache import Renderer

from . import log, conf, pretty_json, gh, lock

dry_run = False
ssh_opts = '-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null'

Scope = namedtuple('Scope', 'name, tpldir, repo')
scopes = [
    Scope('sd', 'superdesk', 'superdesk/superdesk'),
    Scope('sds', 'superdesk-server', 'superdesk/superdesk-core'),
    Scope('sdc', 'superdesk-client', 'superdesk/superdesk-client-core'),
    Scope('sdp', 'superdesk-planning', 'superdesk/superdesk-planning'),
    Scope('ntb', 'superdesk', 'superdesk/superdesk-ntb'),
    Scope('lb', 'liveblog', 'liveblog/liveblog'),
]
scopes = namedtuple('Scopes', [i[0] for i in scopes])(*[i for i in scopes])
checks = {
    scopes.sd.name: ('npmtest', 'flake8'),
    scopes.sds.name: ('flake8', 'nose', 'behave'),
    scopes.sdc.name: ('npmtest', 'e2e--part1', 'e2e--part2'),
}


class Ref(namedtuple('Ref', 'scope, val, uid, sha')):
    __slots__ = ()

    def __new__(cls, scope, ref, sha=None):
        scope = getattr(scopes, scope)
        if ref.startswith('pull/'):
            uid = ('pr', re.sub('[^0-9]', '', ref))
        elif ref.startswith('tags/'):
            uid = ('tag', re.sub('^tags/', '', ref))
        else:
            ref = re.sub('^heads/', '', ref)
            uid = ('', ref)
            ref = 'heads/' + ref

        uid = '%s%s-%s' % (scope.name, uid[0], re.sub('[^a-z0-9]', '', uid[1]))
        ref = super().__new__(cls, scope, ref, uid, sha)
        if not sha:
            sha = gh.get_sha(ref)
            ref = ref._replace(sha=sha)
        return ref

    def __str__(self):
        return 'Ref(uid=%s ref=%r sha=%s)' % (self.uid, self.val, self.sha)

    def __repr__(self):
        return str(self)

    @property
    def is_pr(self):
        return re.match('^pull/\d*$', self.val)


class Logs(namedtuple('Logs', 'path, www')):
    __slots__ = ()

    def __new__(cls, uid):
        root = Path(conf['log_root'])
        path = (
            'all/{time:%Y%m%d-%H%M%S}-{rand:02d}-{uid}/'
            .format(
                uid=uid,
                time=dt.datetime.now(),
                rand=random.randint(0, 99)
            )
        )
        current = root / path
        current.mkdir(parents=True, exist_ok=True)
        previous = current / 'previous'

        latest = root / 'latest' / uid
        latest.parent.mkdir(parents=True, exist_ok=True)
        if latest.exists():
            previous.exists() or previous.symlink_to(latest.resolve())
            latest.unlink()
        latest.symlink_to(current)

        return super().__new__(cls, path, str(root / 'www' / uid))

    def file(self, target):
        return Path(conf['log_root']) / self.path / target

    def url(self, target=''):
        return conf['log_url'] + self.path + target


def render_tpl(tpl, ctx, search_dirs=None):
    if search_dirs is None:
        search_dirs = 'tpl'
    kw = {
        'file_extension': False,
        'search_dirs': search_dirs,
        'missing_tags': 'strict'
    }
    renderer = Renderer(**kw)
    return renderer.render(tpl, ctx)


def endpoint(tpl, scope=None, *, expand=None):
    def val(name, default=None):
        if name in expand:
            return expand.pop(name)
        return default

    def get_ctx(name, scope):
        repo = '/opt/%s' % name
        repo_env = '%s/env' % repo
        repo_core = val('repo_core', '')
        repo_ref = val('repo_ref') or 'heads/master'
        repo_sha = val('repo_sha', '')
        repo_remote = val('repo_remote') or (
            'https://github.com/superdesk/superdesk.git'
        )
        repo_server = val('repo_server', '%s/server' % repo)
        repo_client = val('repo_client', '%s/client' % repo)

        dev = val('dev', True) and 1 or ''
        testing = val('testing') and 1 or ''
        host = val('host', 'localhost')
        host_ssl = val('host_ssl', False) and 1 or ''
        host_url = 'http%s://%s/' % (host_ssl and 's', host)
        db_host = val('db_host', 'localhost')
        db_name = name
        db_optimize = val('db_optimize', dev)
        db_local = db_host == 'localhost'
        test_data = val('test_data') and 1 or ''
        pkg_upgrade = val('pkg_upgrade', False) and 1 or ''
        header_doc = val('header_doc', '')

        is_pr = re.match('^pull/\d*$', repo_ref)
        is_superdesk = name == 'superdesk'
        logs = '/var/log/%s' % name
        config = '/etc/%s.sh' % name
        return locals()

    scope = scope or expand.get('scope')
    scope = getattr(scopes, scope) if scope else scopes[0]

    search_dirs = ['tpl/' + scopes[0].tpldir, 'tpl']
    if scope != scopes[0]:
        search_dirs.insert(0, 'tpl/%s' % scope.tpldir)

    name = 'superdesk'
    ctx = {}
    if scope == scopes.sds:
        repo = '/opt/superdesk/server-core'
        ctx = {
            'repo_core': repo,
            'repo_server': repo,
        }
    elif scope == scopes.sdc:
        repo = '/opt/superdesk/client-core'
        ctx = {
            'repo_core': repo,
            'repo_client': repo,
            'repo_server': '%s/test-server' % repo,
        }
    elif scope == scopes.sdp:
        repo = '/opt/superdesk/planning'
        ctx = {
            'repo_core': repo,
        }
    elif scope == scopes.ntb:
        ctx = {
            'repo_remote': 'https://github.com/superdesk/superdesk-ntb.git',
            'test_data': 0,
        }
    elif scope == scopes.lb:
        name = 'liveblog'
        ctx = {
            'repo_remote': 'https://github.com/liveblog/liveblog.git'
        }

    expand = dict(expand or {}, **ctx)
    ctx = get_ctx(name, scope.name)
    if expand:
        ctx.update(expand)
    tpl = '{{>header.sh}}\n' + tpl
    return render_tpl(tpl, ctx, search_dirs)


def sh(cmd, log_file=None, exit=True, header=True, quiet=False):
    if header:
        cmd = 'set -eux\n%s' % cmd
    if log_file:
        cmd = (
            '(time ({cmd})) 2>&1'
            '  | tee -a {path}'
            '  | aha -w --black >> {path}.htm;'
            '[ "0" = "${{PIPESTATUS[0]}}" ] && true'
            .format(cmd=cmd, path=log_file)
        )

    if not quiet or dry_run:
        print(cmd)
    if dry_run:
        log.info('Dry run!')
        return 0

    code = sp.call(cmd, executable='/bin/bash', shell=True)
    if exit and code:
        raise SystemExit(code)
    return code


def run_job(target, tpl, ctx, logs):
    started = time.time()
    gh.post_status(target, ctx, logs)
    cmd = endpoint(tpl, expand=ctx)
    log_file = logs.file(target + '.log')
    log_url = logs.url(target + '.log')
    log.info('pending: url=%s', log_url)
    logs.file(target + '.sh').write_text(cmd)
    try:
        code = sh(cmd, log_file, exit=False, quiet=True)
        error = None if code == 0 else 'failure: code=%s' % code
    except Exception as e:
        logs.file(target + '.exception').write_text(e)
        error = e
    finally:
        duration = time.time() - started
        duration = '%dm%ds' % (duration // 60, duration % 60)
        info = 'duration=%s url=%s' % (duration, log_url)
        if error:
            log.error('%s %s', error, info)
        else:
            log.info('success: %s', info)

    gh.post_status(target, ctx, logs, code=code, duration=duration)
    return code


def run_jobs_with_lock(scope, ref, targets, all=False):
    ref = Ref(scope, ref)

    with lock.kill_previous('fire_run_jobs:{0.uid}:'.format(ref)):
        run_jobs(ref, targets, all)


def run_jobs(ref, targets, all=False):
    def ctx(_ref, _logs):
        started = time.time()
        uid = _ref.uid
        scope = _ref.scope.name
        repo_ref = _ref.val
        repo_name = _ref.scope.repo
        repo_sha = _ref.sha
        lxc_base = conf['lxc_base']
        lxc_build = '%s--build' % uid
        host = '%s.%s' % (uid, conf['domain'])
        host_ssl = not _ref.is_pr
        host_logs = _logs.www
        logs_url = '%swww/%s' % (conf['log_url'], uid)
        db_host = conf['lxc_data']
        db_name = uid
        test_data = 1
        ssh = 'ssh %s' % ssh_opts
        restart_url = (
            'http://{domain}{url_prefix}/{ref.scope.name}/{ref.val}/restart'
            .format(
                domain=conf['domain'],
                url_prefix=conf['url_prefix'],
                ref=_ref
            )
        )
        del _ref, _logs
        return locals()

    logs = Logs(ref.uid)
    ctx = ctx(ref, logs)
    codes = []

    default_targets = (
        ['build', 'www'] +
        ['check-' + i for i in checks.get(ref.scope.name, ())]
    )
    if targets is None:
        failed_targets = gh.clean_statuses(ref, default_targets, logs)
        targets = default_targets if all else failed_targets
        targets = targets or default_targets
    else:
        targets = [t for t in targets if t in default_targets]

    for target in targets:
        if target == 'build':
            continue
        gh.post_status(target, ctx, logs, started=False)

    target = 'build'
    ctx.update(clean_build='')
    if target in targets:
        targets.remove(target)
        ctx.update(clean_build=1)
    code = run_job(target, '{{>ci-build.sh}}', ctx, logs)
    if code != 0:
        log.error('%s %s', target, ctx['uid'])
        raise SystemExit(code)
    codes.append((target, code))

    jobs = {}
    with futures.ThreadPoolExecutor() as pool:
        target = 'www'
        if target in targets:
            targets.remove(target)
            j = pool.submit(run_job, target, '{{>ci-www.sh}}', ctx, logs)
            jobs[j] = target

        for target in targets:
            # TODO: it should be moved to a better place
            if ref.scope == scopes.sds:
                db_host = 'localhost'
                db_name = 'superdesk'
            else:
                db_host = conf['lxc_data'] + '--tests'
                db_name = '%s--%s' % (ref.uid, target)
            ctx = dict(ctx, db_host=db_host, db_name=db_name, testing=1)
            inner = endpoint('{{>%s.sh}}' % target, expand=ctx)
            c = dict(ctx, target=target, inner=inner)
            j = pool.submit(run_job, target, '{{>ci-check.sh}}', c, logs)
            jobs[j] = target

    for f in futures.as_completed(jobs):
        target = jobs[f]
        try:
            code = f.result()
        except Exception as exc:
            log.exception('%s ctx=%s', exc, pretty_json(ctx))
        else:
            codes.append((target, code))

    code = 1 if [i[1] for i in codes if i[1] != 0] else 0
    state = 'failure' if code else 'success'
    log.info('%s: %s', state, ' '.join('%s=%s' % i for i in codes))
    if code:
        raise SystemExit(code)


def gen_files():
    def gen(scope, ref):
        for target in ['build', 'deploy', 'install']:
            txt = endpoint('{{>%s.sh}}' % target, scope.name, expand={
                'dev': False,
                'header_doc': (
                    '# NOTE: This file is generated by script.\n'
                    '# Modify "tpl/*" and run "./fire gen-files"\n'
                ),
                'repo_ref': ref
            })
            p = Path('files') / scope.tpldir / target
            p.write_text(txt)
            print('+ updated "%s"' % p)

    for name, ref in [(scopes.sd, 'heads/1.0'), (scopes.lb, 'heads/master')]:
        gen(name, ref)


def lxc_ls(opts):
    names = sp.check_output('lxc-ls -1 %s' % opts, shell=True)
    return sorted(names.decode().split())


def mongo_ls(pattern):
    c = '''
    echo "show databases" | mongo --host data-sd | grep -oE "%s" || true
    ''' % pattern
    names = sp.check_output(c, shell=True)
    return sorted(set(names.decode().split()))


def nginx(scope, ssl=False, live=False, reload=True):
    if not scope:
        for scope in scopes:
            nginx(scope.name, ssl=True, live=live, reload=False)
            nginx(scope.name + 'pr', reload=False)
        sh('nginx -s reload')
        return

    scope = scope.split('-', 1)[0]
    names = lxc_ls('--filter="^%s-[a-z0-9]*$" --running' % scope)
    hosts = [{
        'name': n,
        'host': '%s.%s' % (n, conf['domain'])
    } for n in names]
    txt = render_tpl('{{>ci-nginx.sh}}', {
        'scope': scope,
        'ssl': ssl,
        'live': live and 1 or '',
        'hosts': hosts,
        'reload': reload,
    })
    sh(txt, quiet=True)


def gh_clean(scope, using_mongo=False):
    """
    Remove contaner and related databases if
    - pull request was closed
    - branch was removed
    otherwise keep container and related databases alive
    """
    def skip(prefix, ref):
        name = re.sub('[^a-z0-9]', '', str(ref))
        name = '%s-%s' % (prefix, name)
        skips.append('^%s$' % name)
        # sh('lxc-start -n %s || true' % name)

    def ls_names(scope):
        pattern = '^%s(pr)?-[a-z0-9-]*' % scope
        if using_mongo:
            return mongo_ls(pattern)
        else:
            return lxc_ls('--filter="%s"' % pattern)

    scopes_ = [getattr(scopes, s) for s in scope] if scope else scopes
    for s in scopes_:
        skips = []
        for i in gh.call('repos/%s/branches?per_page=100' % s.repo):
            skip(s.name, i['name'])
        for i in gh.call('repos/%s/pulls?state=open&per_page=100' % s.repo):
            skip(s.name + 'pr', i['number'])

        skips = '(%s)' % '|'.join(skips)
        clean = [n for n in ls_names(s.name) if not re.match(skips, n)]
        if not clean:
            log.info('%s: nothing to clean', s.name)
            continue

        sh('''
        ./fire lxc-rm {0}
        ./fire ci-nginx {1} --ssl
        ./fire ci-nginx {1}pr
        '''.format(' '.join(clean), s.name))


def gh_hook(path, url):
    from fireq import web

    path = Path(path)
    headers, body = json.loads(path.read_text())
    data = json.dumps(body, indent=2, sort_keys=True).encode()
    headers['X-Hub-Signature'] = web.get_signature(data)
    headers['Content-Length'] = len(data)
    req = urllib.request.Request(url, data, headers)
    try:
        resp = urllib.request.urlopen(req)
        log.info('%s: %s', resp.status, resp.reason)
    except Exception as e:
        log.error(e)


def main(args=None):
    global dry_run

    formatter = argparse.ArgumentDefaultsHelpFormatter
    parser = argparse.ArgumentParser('fire', argparse.SUPPRESS, add_help=False)
    cmds = parser.add_subparsers(prog='fire')

    def cmd(name, **kw):
        kw.setdefault('formatter_class', formatter)
        p = cmds.add_parser(name, **kw)
        p.set_defaults(cmd=name)
        p.arg = lambda *a, **kw: p.add_argument(*a, **kw) and p
        p.exe = lambda f: p.set_defaults(exe=f) and p

        p.arg('--dry-run', action='store_true')
        return p

    def exit(code=0):
        print('\n'.join(
            ['commands:'] +
            [
                '  {:<12} {}'.format(a.dest, a.help)
                for a in cmds._choices_actions
            ]
        ))
        parser.exit(code)

    cmd('gen-files', help='generate install scripts')\
        .exe(lambda a: gen_files())

    cmd('run', help='run endpoint')\
        .arg('name')\
        .arg('--scope', choices=scopes._fields)\
        .arg('--dev', type=bool, default=1)\
        .arg('--host', default='localhost', help='host')\
        .exe(lambda a: print(endpoint('{{>%s.sh}}' % a.name, expand={
            'scope': a.scope,
            'dev': a.dev,
            'host': a.host
        })))

    cmd('ci', help='run CI targets')\
        .arg('scope', choices=scopes._fields)\
        .arg('ref')\
        .arg('-t', '--target', action='append', default=None)\
        .arg('-a', '--all', action='store_true')\
        .exe(lambda a: run_jobs_with_lock(a.scope, a.ref, a.target, a.all))

    cmd('ci-nginx', help='update nginx sites for CI')\
        .arg('scope', nargs='?', help=(
            'scope or lxc name, if lxc name is given then '
            'it\'ll be used to get a scope name'
        ))\
        .arg('--ssl', action='store_true')\
        .arg('--live', action='store_true')\
        .exe(lambda a: nginx(a.scope, a.ssl, a.live))

    cmd('gh-clean', help=(
            'clean containers and databases using info from Github'
        ))\
        .arg('-s', '--scope', choices=scopes._fields, action='append')\
        .arg('--using-mongo', action='store_true')\
        .exe(lambda a: gh_clean(a.scope, a.using_mongo))

    cmd('gh-hook', help='run webhook with saved request from Github')\
        .arg('path')\
        .arg('url', nargs='?', default='http://localhost:8081/dev/hook')\
        .exe(lambda a: gh_hook(a.path, a.url))

    cmd('lxc-ssh', help='login to LXC container via SSH')\
        .arg('name')\
        .arg('-c', '--cmd', default='')\
        .exe(lambda a: sh(
            'ssh {ssh_opts} $(lxc-info -n {name} -iH) {cmd}'
            .format(ssh_opts=ssh_opts, name=a.name, cmd=a.cmd)
        ))

    cmd('lxc-wait', help='wait when LXC container is ready for SSH login')\
        .arg('name')\
        .arg('--start', action='store_true')\
        .exe(lambda a: sh(render_tpl('{{>lxc-wait.sh}}', {
            'name': a.name,
            'start': a.start and 1 or ''
        })))

    cmd('lxc-init', help=(
            'create minimal LXC container with SSH and root keys'
        ))\
        .arg('name')\
        .arg(
            '-k', '--keys', default='/root/.ssh/id_rsa.pub',
            help='authorized keys'
        )\
        .arg('-o', '--opts', default='-B zfs', help='lxc-create options')\
        .exe(lambda a: sh(render_tpl('{{>lxc-init.sh}}', {
            'name': a.name,
            'keys': a.keys,
            'opts': a.opts,
        })))

    cmd('lxc-data', help='create LXC container with data services')\
        .arg('name')\
        .arg('--tests', action='store_true')\
        .exe(lambda a: sh('''
        ./fire lxc-init {0}
        ./fire run add-dbs --dev={1} | ./fire lxc-ssh {0}
        '''.format(a.name, a.tests and 1 or '')))

    cmd('lxc-rm', help='remove LXC containers and related databases')\
        .arg('n', nargs='+')\
        .exe(lambda a: sh(render_tpl('{{>lxc-rm.sh}}', {
            'names': a.n,
            'db_host': conf['lxc_data']
        }), quiet=True))

    cmd('lxc-expose', help='expose 80 port from LXC container')\
        .arg('name')\
        .arg('domain')\
        .arg('-c', '--clean', action='store_true')\
        .exe(lambda a: sh(render_tpl('{{>lxc-expose.sh}}', {
            'name': a.name,
            'domain': a.domain,
            'clean': a.clean and 1 or ''
        })))

    args, extra = parser.parse_known_args(args)
    if extra in (['-h'], ['--help']):
        exit()
    elif extra:
        print('unrecognized arguments: %s\n' % ' '.join(extra))
        exit(1)
    elif not hasattr(args, 'exe'):
        exit(1)

    dry_run = getattr(args, 'dry_run', dry_run)
    if dry_run:
        conf['no_statuses'] = True

    args.exe(args)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        raise SystemExit('^C')
