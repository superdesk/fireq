from firelib.cli import Ref, scopes
from firelib.gh import Error


def test_base():
    ref = Ref('sd', 'heads/master')
    assert ref.scope == scopes.sd
    assert ref.uid == 'sd-master'
    assert ref.val == 'heads/master'

    ref = Ref('lb', 'feature-freetypes')
    assert ref.scope == scopes.lb
    assert ref.uid == 'lb-featurefreetypes'
    assert ref.val == 'heads/feature-freetypes'

    ref = Ref('sdc', 'pull/10/head')
    assert ref.scope == scopes.sdc
    assert ref.uid == 'sdcpr-10'
    assert ref.val == 'pull/10/head'

    ref = Ref('sds', 'pull/10')
    assert ref.scope == scopes.sds
    assert ref.uid == 'sdspr-10'
    assert ref.val == 'pull/10'

    ref = Ref('sd', 'tags/v1.0')
    assert ref.scope == scopes.sd
    assert ref.uid == 'sdtag-v10'
    assert ref.val == 'tags/v1.0'


def test_sha(gh_call, load_json, raises):
    gh_call.return_value = load_json('gh_sha-sds_master.json')
    ref = Ref('sds', 'master')
    assert gh_call.called
    assert gh_call.call_args == (
        ('repos/superdesk/superdesk-core/git/refs/heads/master',), {}
    )
    assert ref.sha == '4551c93bef57e8397d675274569feb8b78a834f8'

    gh_call.reset_mock()
    gh_call.return_value = load_json('gh_sha-sd_pull_1991_head.json')
    ref = Ref('sd', 'pull/1991')
    assert gh_call.called
    assert gh_call.call_args == (
        ('repos/superdesk/superdesk/git/refs/pull/1991/head',), {}
    )
    assert ref.sha == '1c709766c81ed534f0291a2304280d6427adcd01'

    gh_call.reset_mock()
    gh_call.return_value = load_json('gh_sha-sd_pull_1991_head.json')
    ref = Ref('sd', 'pull/1991/head')
    assert gh_call.called
    assert gh_call.call_args == (
        ('repos/superdesk/superdesk/git/refs/pull/1991/head',), {}
    )
    assert ref.sha == '1c709766c81ed534f0291a2304280d6427adcd01'

    gh_call.reset_mock()
    gh_call.return_value = load_json('gh_sha-sd_pull_1991_merge.json')
    ref = Ref('sd', 'pull/1991/merge')
    assert gh_call.called
    assert gh_call.call_args == (
        ('repos/superdesk/superdesk/git/refs/pull/1991/merge',), {}
    )
    assert ref.sha == '59ad6aaac17b5e476015cbb861b4d0685770cdc4'

    gh_call.reset_mock()
    gh_call.side_effect = Error
    with raises(Error):
        ref = Ref('sds', 'pull/1000000000')


def test_sha__real_http(raises, real_http, gh_call):
    gh_call._stop()
    ref = Ref('sds', 'master')
    assert ref.sha

    with raises(Error):
        ref = Ref('sds', 'pull/1000000000')
