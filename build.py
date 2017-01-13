from pathlib import Path

from pystache import Renderer


def render_tpl(tpl, ctx):
    kw = {
        'file_extension': False,
        'search_dirs': ['tpl/superdesk', 'tpl'],
        'missing_tags': 'strict'
    }
    renderer = Renderer(**kw)
    return renderer.render(tpl, ctx)


def main():
    def ctx():
        is_pr = False
        name = 'superdesk'
        repo = '/opt/%s' % name
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
        return locals()

    for target in ['build', 'deploy', 'install']:
        tpl = (
            '{{>header.sh}}'
            '{{>superdesk/%s.sh}}'
        ) % target
        txt = render_tpl(tpl, ctx())
        Path('files/superdesk/%s' % target).write_text(txt)


if __name__ == '__main__':
    main()
