import textwrap
import subprocess


def check_output(cmd):
    return subprocess.check_output(cmd, shell=True).decode()


def startswith(cmd, txt):
    txt = textwrap.dedent(txt).strip()
    txt = txt % {'scopes': '{sd,sds,sdc,sdp,ntb,lb}'}
    out = check_output(cmd)
    if out.startswith('running with sudo...\n\n'):
        out = out.split('\n\n', 1)[1]
    assert out.startswith(txt)


def test_fire_wrapper():
    startswith('./fire gen-files -h', (
        'usage: fire gen-files [-h] [--dry-run]'
    ))

    startswith('./fire ci -h', (
        'usage: fire ci [-h] [--dry-run] [-t TARGET] [-a] %(scopes)s ref'
    ))

    startswith('./fire run -h', '''
    usage: fire run [-h] [--dry-run] [--scope %(scopes)s] [--dev DEV]
                    [--host HOST]
                    name
    ''')
