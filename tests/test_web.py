from unittest.mock import patch

from fireq import web


@patch('fireq.gh.call')
def test_hook_ctx(_gh, load_json):
    push = load_json('web_hook-sd_master_push.json')
    assert web.get_hook_ctx(*push)
    assert not _gh.called

    push[1]['after'] = '0000000000000000000000000000000000000000'
    assert not web.get_hook_ctx(*push)
    assert not _gh.called

    # pull_request
    pr = load_json('web_hook-sdpr_2444.json')
    assert web.get_hook_ctx(*pr)
    assert not _gh.called

    pr[1]['action'] = 'reopened'
    assert web.get_hook_ctx(*pr)
    assert not _gh.called

    pr[1]['action'] = 'synchronize'
    assert web.get_hook_ctx(*pr)
    assert not _gh.called

    pr[1]['action'] = 'close'
    assert not web.get_hook_ctx(*pr)
    assert not _gh.called
