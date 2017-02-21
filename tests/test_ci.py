import re


def test_www(main, capfd):
    main('ci sd naspeh -t www --dry-run')
    out, err = capfd.readouterr()
    mount, = re.findall(r'(?m)^lxc\.mount\.entry.*', out)
    assert '/tmp/fireq/logs/www/sd-naspeh ${logs:1}' in mount
    logs, = re.findall(r'(?m)^logs=.*', out)
    assert 'logs=/var/log/superdesk' == logs
