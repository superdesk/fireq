def test_www(sh):
    out = sh('./fire2 ci sd naspeh -t www --dry-run| grep -3 ^lxc.mount.entry')
    assert '/tmp/fire-logs/www/sd-naspeh ${logs:1}' in out
    assert 'logs=/var/log/superdesk' in out
