import argparse
import datetime as dt
import os
import random
import subprocess
from pathlib import Path

from pystache import Renderer

from api import log

dry_run = False
ssh_opts = '-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null'


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


def render(target, *, expand=None):
    def get_ctx(name):
        dev = False
        is_pr = False
        repo = '/opt/%s' % name
        repo_core = ''
        repo_ref = 'heads/master'
        repo_sha = ''
        repo_remote = 'https://github.com/superdesk/superdesk.git'
        repo_server = '%s/server' % repo
        repo_client = '%s/client' % repo
        repo_env = '%s/env' % repo

        # deploy
        is_superdesk = name == 'superdesk'
        host = 'localhost'
        logs = '/var/log/%s' % name
        config = '/etc/%s.sh' % name
        pkg_upgrade = ''
        db_optimize = False
        header_doc = ''
        return locals()

    target = target.split('/')
    search_dirs = [
        'tpl/superdesk',
        'tpl'
    ]
    if len(target) == 2:
        scope, target = target
        search_dirs.insert(0, 'tpl/%s' % scope)
    else:
        scope, target = None, target[0]

    ctx = {}
    name = 'superdesk'
    if scope == 'superdesk-server':
        repo = '/opt/superdesk/server-core'
        ctx = {
            'dev': True,
            'repo_core': repo,
            'repo_server': repo,
            'db_optimize': True,
        }
    elif scope == 'superdesk-client':
        repo = '/opt/superdesk/client-core'
        ctx = {
            'dev': True,
            'repo_core': repo,
            'repo_client': repo,
            'repo_server': '%s/test-server' % repo,
            'db_optimize': True,
        }
    elif scope == 'liveblog':
        name = scope
        ctx = {
            'repo_remote': 'https://github.com/liveblog/liveblog.git'
        }

    tpl = (
        '{{>header.sh}}'
        '{{>%s.sh}}'
        % target
    )
    ctx = dict(get_ctx(name), **ctx)
    if expand is not None:
        ctx.update(expand)
    return render_tpl(tpl, ctx, search_dirs)


def sh(cmd, ctx, log_file=None, exit=True):
    if ctx is not None:
        cmd = render_tpl(cmd, ctx)

    cmd = 'set -eux; %s' % cmd
    if log_file:
        cmd = (
            '(time ({cmd})) 2>&1'
            '  | tee -a {path}'
            '  | aha -w --black >> {path}.htm;'
            '[ "0" = "${{PIPESTATUS[0]}}" ] && true'
            .format(cmd=cmd, path=log_file)
        )

    log.info(cmd)
    if dry_run:
        log.info('Dry run!')
        return 0

    code = subprocess.call(cmd, executable='/bin/bash', shell=True)
    if exit and code:
        raise SystemExit(code)
    return code


def run_ci():
    from concurrent import futures

    def ctx():
        ref = 'heads/master'
        name = 'dev-sd'
        lxc_build = '%s--build' % name
        lxc_base = 'base-sd--4'
        ssh = 'ssh %s' % ssh_opts
        logs = '/tmp/logs/www/%s' % name
        return locals()

    ctx = ctx()
    log_path = (
        '/tmp/logs/sd-{0}/{time:%Y%m%d-%H%M%S}-{rand:02d}--{1}/'
        .format(
            *ctx['ref'].split('/', 1),
            time=dt.datetime.now(),
            rand=random.randint(0, 99)
        )
    )
    os.makedirs(log_path, exist_ok=True)
    os.makedirs(ctx['logs'], exist_ok=True)

    sh('''
    (lxc-ls -1\
        | grep "^{{name}}--"\
        | grep -v "^{{lxc_build}}$"\
        | sort -r\
        | xargs -r ./fire lxc-rm) || true;
    lxc={{lxc_build}};
    ./fire lxc-copy -rsc -b {{lxc_base}} $lxc;
    ./fire2 run superdesk/build | {{ssh}} $lxc;
    lxc-stop -n $lxc
    ''', ctx, log_path + 'build.log')

    check = '''
    lxc="{{name}}--{{target}}";
    ./fire lxc-copy -rcs -b {{lxc_build}} $lxc
    ./fire2 run superdesk/{{target}} | {{ssh}} $lxc
    '''

    www = '{{>ci/www.sh}}'

    with futures.ThreadPoolExecutor() as pool:
        jobs = {}
        for t in ['flake8', 'nose', 'behave', 'npmtest']:
            target = 'check-%s' % t
            log_file = log_path + target + '.log'
            c = dict(ctx, target=target)
            jobs[pool.submit(sh, check, c, log_file, exit=False)] = {
                'log_file': log_file,
                'target': target
            }

        log_file = log_path + 'www.log'
        jobs[pool.submit(sh, www, ctx, log_file, exit=False)] = {
            'log_file': log_file,
            'target': 'www'
        }

    for f in futures.as_completed(jobs):
        ctx = jobs[f]
        try:
            code = f.result()
        except Exception as exc:
            log.exception(ctx, exc)
        else:
            ctx.update(code=code)
            log.info('target=%(target)s code=%(code)s log=%(log_file)s', ctx)


def gen_files():
    def gen(name):
        for target in ['build', 'deploy', 'install']:
            path = '%s/%s' % (name, target)
            txt = render(path, expand={'header_doc': (
                '# NOTE: This file is generated by script.\n'
                '# Modify "tpl/*" and run "./fire gen-files"'
            )})
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
        .arg('endpoint')\
        .exe(lambda a: print(render(a.endpoint)))

    cmd('ci')\
        .exe(lambda a: run_ci())

    args = parser.parse_args()
    dry_run = getattr(args, 'dry_run', dry_run)
    if not hasattr(args, 'exe'):
        parser.print_usage()
    else:
        args.exe(args)


if __name__ == '__main__':
    main()
