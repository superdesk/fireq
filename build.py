import argparse
import datetime as dt
import random
import re
import subprocess
from concurrent import futures
from pathlib import Path

from pystache import Renderer

from api import log

dry_run = False
ssh_opts = '-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null'
tpl_ci_check = '''
lxc="{{lxc_www}}--{{target}}";
./fire lxc-copy -cs -b {{lxc_build}} $lxc
cat <<"EOF2" | {{ssh}} $lxc
{{>header.sh}}
{{>%s.sh}}
EOF2
'''


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

    search_dirs = ['tpl/superdesk', 'tpl/']
    scope = scope or expand.get('scope')
    if scope and scope != 'superdesk':
        search_dirs.insert(0, 'tpl/%s' % scope)

    name = 'superdesk'
    ctx = {}
    if scope == 'superdesk-server':
        repo = '/opt/superdesk/server-core'
        ctx = {
            'repo_core': repo,
            'repo_server': repo,
            'db_host': 'localhost',
        }
    elif scope == 'superdesk-client':
        repo = '/opt/superdesk/client-core'
        ctx = {
            'repo_core': repo,
            'repo_client': repo,
            'repo_server': '%s/test-server' % repo,
        }
    elif scope == 'liveblog':
        name = scope
        ctx = {
            'repo_remote': 'https://github.com/liveblog/liveblog.git'
        }

    expand = expand or {}
    expand.update(ctx)
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
        log.info('code=%s (%s/%s)', code, ctx['id'], target)
    except Exception as e:
        log.error(e)
        code = 1
    return code


def run_jobs(targets=None, scope='superdesk'):
    def ctx(scope):
        lxc_www = 'dev-sd'
        lxc_base = 'base-sd--dev'
        lxc_build = '%s--build' % lxc_www
        host = '%s.test.superdesk.org' % lxc_www
        host_logs = '/tmp/logs/www/%s' % lxc_www
        db_host = 'data-dev'
        db_name = lxc_www
        ref = 'heads/naspeh'
        ssh = 'ssh %s' % ssh_opts
        id = '%s/%s' % (scope, ref)
        return locals()

    ctx = ctx(scope)
    ref = ctx['ref'].split('/', 1)
    log_path = Path(
        '/tmp/logs/sd-{0}/{time:%Y%m%d-%H%M%S}-{rand:02d}--{1}/'
        .format(
            *ref,
            time=dt.datetime.now(),
            rand=random.randint(0, 99)
        )
    )
    log_path.mkdir(parents=True, exist_ok=True)
    latest = log_path.parent / 'latest-{1}'.format(*ref)
    latest.exists() and latest.unlink()
    latest.symlink_to(log_path)

    if targets is None:
        targets = ['build', 'www']

    target = 'build'
    if target in targets:
        targets.remove(target)
        run_job(target, '{{>ci-build.sh}}', ctx, log_path)

    jobs = {}
    with futures.ThreadPoolExecutor() as pool:
        target = 'www'
        if target in targets:
            targets.remove(target)
            j = pool.submit(run_job, target, '{{>ci-www.sh}}', ctx, log_path)
            jobs[j] = ctx

        for target in targets:
            tpl = tpl_ci_check % target
            c = dict(ctx, target=target)
            j = pool.submit(run_job, target, tpl, c, log_path)
            jobs[j] = c

    for f in futures.as_completed(jobs):
        ctx = jobs[f]
        try:
            f.result()
        except Exception as exc:
            log.exception(ctx, exc)


def gen_files():
    def gen(name):
        for target in ['build', 'deploy', 'install']:
            path = '%s/%s' % (name, target)
            txt = endpoint('{{>%s.sh}}' % target, expand={
                'dev': False,
                'scope': name,
                'header_doc': (
                    '# NOTE: This file is generated by script.\n'
                    '# Modify "tpl/*" and run "./fire gen-files"\n'
                )
            })
            p = Path('files/%s' % path)
            p.write_text(txt)
            print('+ updated "%s"' % p)

    for name in ['superdesk', 'liveblog']:
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
        .arg('--scope', default='superdesk')\
        .arg('--dev', type=bool, default=True)\
        .arg('--host', default='localhost')\
        .exe(lambda a: print(endpoint('{{>%s.sh}}' % a.name, expand={
            'scope': a.scope,
            'dev': a.dev,
            'host': a.host
        })))

    cmd('ci')\
        .arg('--scope', default='superdesk')\
        .arg('-t', '--target', action='append', default=None)\
        .exe(lambda a: run_jobs(a.target, a.scope))

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
