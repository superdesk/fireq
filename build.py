from pathlib import Path

from pystache import Renderer


def render_tpl(tpl, ctx, search_dirs=None):
    if search_dirs is None:
        search_dirs = [
            'tpl/superdesk',
            'tpl'
        ]
    kw = {
        'file_extension': False,
        'search_dirs': search_dirs,
        'missing_tags': 'strict'
    }
    renderer = Renderer(**kw)
    return renderer.render(tpl, ctx)


def render(name, *, search_dirs=None, expand=None):
    def get_ctx():
        dev = False
        is_pr = False
        name = 'superdesk'
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
        return locals()

    tpl = (
        '{{>header.sh}}'
        '{{>%s.sh}}'
        % name
    )

    ctx = get_ctx()
    if expand is not None:
        ctx.update(expand)
    return render_tpl(tpl, ctx, search_dirs)


def main():
    import sys

    if len(sys.argv) == 1:
        for target in ['build', 'deploy', 'install']:
            txt = render('superdesk/%s' % target)
            Path('files/superdesk/%s' % target).write_text(txt)
    else:
        target = sys.argv[1].split('/')
        search_dirs = [
            'tpl/superdesk',
            'tpl'
        ]
        if len(target) == 2:
            scope, name = target
            search_dirs.insert(0, 'tpl/%s' % scope)
        else:
            scope, name = None, target[0]

        expand = None
        if scope == 'superdesk-server':
            repo = '/opt/superdesk/server-core'
            expand = {
                'dev': True,
                'repo_core': repo,
                'repo_server': repo,
                'db_optimize': True,
            }
        elif scope == 'superdesk-client':
            repo = '/opt/superdesk/client-core'
            expand = {
                'dev': True,
                'repo_core': repo,
                'repo_client': repo,
                'repo_server': '%s/test-server' % repo,
                'db_optimize': True,
            }
        txt = render(name, expand=expand, search_dirs=search_dirs)
        print(txt)


if __name__ == '__main__':
    main()
