from unittest.mock import patch

# patched in conftest.py:pytest_runtest_setup
logs = 'http://localhost/logs/all/20170101-000000-00'


@patch.dict('firelib.cli.conf', {'no_statuses': False})
@patch('firelib.gh.get_sha', lambda *a: '<sha>')
def test_base(gh_call, sp, main, raises):
    gh_call.return_value = {}

    main('ci sds master -t build')
    assert gh_call.call_count == 4
    a1, a2, a3, a4 = gh_call.call_args_list
    assert a1[0] == (
        'repos/superdesk/superdesk-core/statuses/<sha>',
        {
            'description': 'click "Details" to restart the build',
            'target_url': 'http://localhost/sds/heads/master/restart',
            'context': 'fire:restart',
            'state': 'success'
        }
    )
    assert a2[0] == (
        'repos/superdesk/superdesk-core/statuses/<sha>',
        {
            'description': 'waiting for start',
            'target_url': logs + '-sds-master/',
            'context': 'fire:build',
            'state': 'pending'
        }
    )
    assert a3[0] == (
        'repos/superdesk/superdesk-core/statuses/<sha>',
        {
            'description': '',
            'target_url': logs + '-sds-master/build.log',
            'context': 'fire:build',
            'state': 'pending'
        }
    )
    assert a4[0] == (
        'repos/superdesk/superdesk-core/statuses/<sha>',
        {
            'description': 'duration: 0m0s',
            'target_url': logs + '-sds-master/build.log.htm',
            'context': 'fire:build',
            'state': 'success'
        }
    )

    gh_call.reset_mock()
    main('ci sd master -t www')
    assert gh_call.call_count == 3
    a1, a2, a3 = gh_call.call_args_list
    assert a1[0] == (
        'repos/superdesk/superdesk/statuses/<sha>',
        {
            'description': 'waiting for start',
            'target_url': logs + '-sd-master/',
            'context': 'fire:www',
            'state': 'pending'
        }
    )
    assert a2[0] == (
        'repos/superdesk/superdesk/statuses/<sha>',
        {
            'description': '',
            'target_url': logs + '-sd-master/www.log',
            'context': 'fire:www',
            'state': 'pending'
        }
    )
    assert a3[0] == (
        'repos/superdesk/superdesk/statuses/<sha>',
        {
            'description': 'click "Details" to see the test instance',
            'target_url': 'http://sd-master.localhost',
            'context': 'fire:www',
            'state': 'success'
        }
    )

    gh_call.reset_mock()
    sp.call.return_value = 16
    with raises(SystemExit):
        main('ci sd master -t www')
    assert gh_call.call_count == 3
    a1, a2, a3 = gh_call.call_args_list
    assert a1[0] == (
        'repos/superdesk/superdesk/statuses/<sha>',
        {
            'description': 'waiting for start',
            'target_url': logs + '-sd-master/',
            'context': 'fire:www',
            'state': 'pending'
        }
    )
    assert a2[0] == (
        'repos/superdesk/superdesk/statuses/<sha>',
        {
            'description': '',
            'target_url': logs + '-sd-master/www.log',
            'context': 'fire:www',
            'state': 'pending'
        }
    )
    assert a3[0] == (
        'repos/superdesk/superdesk/statuses/<sha>',
        {
            'description': 'duration: 0m0s',
            'target_url': logs + '-sd-master/www.log.htm',
            'context': 'fire:www',
            'state': 'failure'
        }
    )

    # should be all pending statuses in the begining
    gh_call.reset_mock()
    sp.call.return_value = 0
    main('ci sd master')
    assert gh_call.call_count == 13
    s = [
        (i[0][1]['context'], i[0][1]['state'])
        for i in gh_call.call_args_list
    ]
    assert s[:5] == [
        ('fire:restart', 'success'),

        # pending statuses with general log directory
        ('fire:build', 'pending'),
        ('fire:www', 'pending'),
        ('fire:check-npmtest', 'pending'),
        ('fire:check-flake8', 'pending'),
    ]
    assert set(s[5:]) == {
        ('fire:build', 'pending'),
        ('fire:www', 'pending'),
        ('fire:check-npmtest', 'pending'),
        ('fire:check-flake8', 'pending'),

        ('fire:build', 'success'),
        ('fire:www', 'success'),
        ('fire:check-npmtest', 'success'),
        ('fire:check-flake8', 'success'),
    }


@patch('firelib.gh.get_sha', lambda *a: '<sha>')
def test_no_statuses(main, raises, capsys, gh_call):
    main('ci sd naspeh')
    assert not gh_call.called

    with patch.dict('firelib.cli.conf', {'no_statuses': False}):
        main('ci sd naspeh --dry-run')
        assert not gh_call.called


def test_base__real_http(sp, capfd, real_http, gh_call, main):
    gh_call._stop()
    with patch.dict('firelib.cli.conf', {'no_statuses': False}):
        main('ci sd naspeh')
        out, err = capfd.readouterr()
        # 1: restart;
        # 2,3,4,5: pending with general log directory
        # 6,7,8,9: pending with particular log file
        # 10,11,12,13: success
        assert 13 == err.count("201 url='https://api.github.com/repos/")

    # no statuses
    main('ci sd naspeh')
    out, err = capfd.readouterr()
    assert 0 == err.count("201 url='https://api.github.com/repos/")
