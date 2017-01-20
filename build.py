import argparse
import datetime as dt
import random
import re
import subprocess
from concurrent import futures
from collections import namedtuple
from pathlib import Path

from pystache import Renderer

from api import log

dry_run = False
ssh_opts = '-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null'

Scope = namedtuple('Scope', 'name, tpldir, repo')
scopes = [
    Scope('sd', 'superdesk', 'superdesk/superdesk'),
    Scope('sds', 'superdesk-server', 'superdesk/superdesk-core'),
    Scope('sdc', 'superdesk-client', 'superdesk/superdesk-client-core'),
    Scope('lb', 'liveblog', 'liveblog/liveblog'),
]
scopes = namedtuple('Scopes', [i[0] for i in scopes])(*[i for i in scopes])
checks = {
    scopes.sd.name: ('npmtest', 'flake8', 'nose', 'behave'),
    scopes.sds.name: ('flake8', 'nose', 'behave'),
    scopes.sdc.name: ('npmtest', 'e2e--part1', 'e2e--part2'),
}


class Ref(namedtuple('Ref', 'scope, val, uid')):
    __slots__ = ()

    def __new__(cls, scope, ref):
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
        uid = 'dev-' + uid

        return super().__new__(cls, scope, ref, uid)


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

    def get_ctx(name):
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

        dev = val('dev', True)
        host = val('host', 'localhost')
        host_ssl = val('host_ssl', False) and 1 or ''
        db_host = val('db_host', 'localhost')
        db_name = name
        db_optimize = val('db_optimize', dev)
        db_local = db_host == 'localhost'
        pkg_upgrade = val('pkg_upgrade', False) and 1 or ''
        header_doc = val('header_doc', '')

        is_pr = re.match('^pulls/\d*$', repo_ref)
        is_superdesk = name == 'superdesk'
        logs = '/var/log/%s' % name
        config = '/etc/%s.sh' % name
        return locals()

    scope = scope or expand.get('scope')
    scope = getattr(scopes, scope) if scope else scopes.sd

    search_dirs = ['tpl/superdesk', 'tpl']
    if scope != scopes.sd:
        search_dirs.insert(0, 'tpl/%s' % scope.tpldir)

    name = 'superdesk'
    ctx = {}
    if scope == scopes.sds:
        repo = '/opt/superdesk/server-core'
        ctx = {
            'repo_core': repo,
            'repo_server': repo,
            'db_host': 'localhost',
        }
    elif scope == scopes.sdc:
        repo = '/opt/superdesk/client-core'
        ctx = {
            'repo_core': repo,
            'repo_client': repo,
            'repo_server': '%s/test-server' % repo,
        }
    elif scope == scopes.lb:
        name = 'liveblog'
        ctx = {
            'repo_remote': 'https://github.com/liveblog/liveblog.git'
        }

    expand = dict(expand or {}, **ctx)
    ctx = get_ctx(name)
    if expand:
        ctx.update(expand)
    tpl = '{{>header.sh}}\n' + tpl
    return render_tpl(tpl, ctx, search_dirs)


def sh(cmd, log_file=None, exit=True, header=True, quiet=False):
    if header:
        cmd = 'set -eux; %s' % cmd
    if log_file:
        cmd = (
            '(time ({cmd})) 2>&1'
            '  | tee -a {path}'
            '  | aha -w --black >> {path}.htm;'
            '[ "0" = "${{PIPESTATUS[0]}}" ] && true'
            .format(cmd=cmd, path=log_file)
        )

    if not quiet:
        log.info(cmd)
    if dry_run:
        log.info('Dry run!')
        return 0

    code = subprocess.call(cmd, executable='/bin/bash', shell=True)
    if exit and code:
        raise SystemExit(code)
    return code


def run_job(target, tpl, ctx, log_path):
    # TODO: add github statuses here
    cmd = endpoint(tpl, expand=ctx)
    log_file = log_path / (target + '.log')
    log.info('log=%s', log_file)
    (log_path / (target + '.sh')).write_text(cmd)
    try:
        code = sh(cmd, log_file, exit=False, quiet=True)
        log.info('code=%s log=%s', code, log_file)
    except Exception as e:
        log.error(e)
        code = 1
    return code


def run_jobs(targets=None, scope=None, ref='master'):
    def ctx(scope, ref):
        uid = ref.uid
        repo_ref = ref.val
        lxc_base = 'base-sd--dev'
        lxc_build = '%s--build' % uid
        host = '%s.test.superdesk.org' % uid
        host_logs = '/tmp/logs/www/%s' % uid
        db_host = 'data-dev'
        db_name = uid
        ssh = 'ssh %s' % ssh_opts
        return locals()

    ref = Ref(scope, ref)
    ctx = ctx(scope, ref)
    log_root = Path('/tmp/logs')
    log_path = log_root / (
        'all/{time:%Y%m%d-%H%M%S}-{rand:02d}-{uid}'
        .format(
            uid=ctx['uid'],
            time=dt.datetime.now(),
            rand=random.randint(0, 99)
        )
    )
    log_path.mkdir(parents=True, exist_ok=True)
    latest = log_root / ('latest/' + ctx['uid'])
    latest.parent.mkdir(parents=True, exist_ok=True)
    latest.exists() and latest.unlink()
    latest.symlink_to(log_path)

    if targets is None:
        targets = (
            ['build', 'www'] +
            ['check-' + i for i in checks.get(scope, ())]
        )

    target = 'build'
    if target in targets:
        targets.remove(target)
        code = run_job(target, '{{>ci-build.sh}}', ctx, log_path)
        if code != 0:
            raise SystemExit(code)

    jobs = {}
    with futures.ThreadPoolExecutor() as pool:
        target = 'www'
        if target in targets:
            targets.remove(target)
            j = pool.submit(run_job, target, '{{>ci-www.sh}}', ctx, log_path)
            jobs[j] = ctx

        for target in targets:
            inner = endpoint('{{>%s.sh}}' % target, expand=ctx)
            c = dict(ctx, target=target, inner=inner)
            j = pool.submit(run_job, target, '{{>ci-check.sh}}', c, log_path)
            jobs[j] = c

    for f in futures.as_completed(jobs):
        ctx = jobs[f]
        try:
            f.result()
        except Exception as exc:
            log.exception(ctx, exc)


def gen_files():
    def gen(scope):
        for target in ['build', 'deploy', 'install']:
            txt = endpoint('{{>%s.sh}}' % target, scope.name, expand={
                'dev': False,
                'header_doc': (
                    '# NOTE: This file is generated by script.\n'
                    '# Modify "tpl/*" and run "./fire gen-files"\n'
                )
            })
            p = Path('files') / scope.tpldir / target
            p.write_text(txt)
            print('+ updated "%s"' % p)

    for name in [scopes.sd, scopes.lb]:
        gen(name)


def main():
    global dry_run

    parser = argparse.ArgumentParser('fire')
    cmds = parser.add_subparsers(help='commands')

    def cmd(name, **kw):
        p = cmds.add_parser(name, **kw)
        p.set_defaults(cmd=name)
        p.arg = lambda *a, **kw: p.add_argument(*a, **kw) and p
        p.exe = lambda f: p.set_defaults(exe=f) and p

        p.arg('--dry-run', action='store_true')
        return p

    cmd('gen-files')\
        .exe(lambda a: gen_files())

    cmd('run', aliases=['r'])\
        .arg('name')\
        .arg('--scope', choices=scopes._fields)\
        .arg('--dev', type=bool, default=True)\
        .arg('--host', default='localhost')\
        .exe(lambda a: print(endpoint('{{>%s.sh}}' % a.name, expand={
            'scope': a.scope,
            'dev': a.dev,
            'host': a.host
        })))

    cmd('ci')\
        .arg('scope', choices=scopes._fields)\
        .arg('ref')\
        .arg('-t', '--target', action='append', default=None)\
        .exe(lambda a: run_jobs(a.target, a.scope, a.ref))

    args = parser.parse_args()
    dry_run = getattr(args, 'dry_run', dry_run)
    if not hasattr(args, 'exe'):
        parser.print_usage()
    else:
        args.exe(args)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        raise SystemExit('^C')
