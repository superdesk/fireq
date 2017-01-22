import textwrap
import subprocess


def check_output(cmd):
    return subprocess.check_output(cmd, shell=True).decode()


def startswith(cmd, txt):
    txt = textwrap.dedent(txt).strip()
    assert check_output(cmd).startswith(txt)


def test_fire_wrapper():
    startswith('./fire2 -h', (
        'usage: fire [-h] {gen-files,run,r,ci}'
    ))
    startswith('./fire2 gen-files -h', (
        'usage: fire gen-files [-h] [--dry-run]'
    ))

    startswith('./fire2 ci -h', (
        'usage: fire ci [-h] [--dry-run] [-t TARGET] {sd,sds,sdc,lb} ref'
    ))

    startswith('./fire2 run -h', '''
    usage: fire run [-h] [--dry-run] [--scope {sd,sds,sdc,lb}] [--dev DEV]
                    [--host HOST]
                    name
    ''')
