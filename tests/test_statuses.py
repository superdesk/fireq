from unittest.mock import patch

# patched in conftest.py:pytest_runtest_setup
logs = 'http://localhost/logs/all/20170101-000000-00'


@patch.dict('firelib.cli.conf', {'no_statuses': False})
@patch('firelib.gh.get_sha', lambda *a: '<sha>')
@patch('firelib.gh.clean_statuses', lambda *a: None)
def test_base(gh_call, sp, main, raises):
    gh_call.return_value = {}

    main('ci sds master -t build')
    assert gh_call.call_count == 3
    a1, a2, a3 = gh_call.call_args_list
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
            'description': '',
            'target_url': logs + '-sds-master/build.log',
            'context': 'fire:build',
            'state': 'pending'
        }
    )
    assert a3[0] == (
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
    assert gh_call.call_count == 12
    s = [
        (i[0][1]['context'], i[0][1]['state'])
        for i in gh_call.call_args_list
    ]
    assert s[:5] == [
        # waiting statuses
        ('fire:www', 'pending'),
        ('fire:check-npmtest', 'pending'),
        ('fire:check-flake8', 'pending'),

        ('fire:restart', 'success'),
        ('fire:build', 'pending'),
    ]
    assert set(s[5:]) == {
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
        #  1: clean "!restart" is not presented anymore
        #  2: success "restart"
        #  3, 4, 5: waiting with general log directory
        #  6, 7, 8, 9: pending with particular log file
        # 10,11,12,13: success
        assert 13 == err.count("201 url='https://api.github.com/repos/")

    # no statuses
    main('ci sd naspeh')
    out, err = capfd.readouterr()
    assert 0 == err.count("201 url='https://api.github.com/repos/")


@patch.dict('firelib.cli.conf', {'no_statuses': False})
@patch('firelib.gh.get_sha', lambda *a: '<sha>')
def test_cleaning(gh_call, main, load_json):
    gh_call.return_value = load_json('status-sdcpr_1282.json')
    main('ci sdc pull/1282')

    def call_args(context):
        return ('repos/superdesk/superdesk-client-core/statuses/<sha>', {
            'description': 'cleaned, is not presented anymore',
            'target_url': logs + '-sdcpr-1282/',
            'context': context,
            'state': 'success'
        })

    a1, a2, a3, a4, a5 = gh_call.call_args_list[:5]
    assert a1[0] == (
        'repos/superdesk/superdesk-client-core/commits/<sha>/status',
    )
    assert a2[0] == call_args('fire:check-docs')
    assert a3[0] == call_args('fire:check-e2e')
    assert a4[0] == call_args('fire:!restart')
    assert a5[0] == (
        'repos/superdesk/superdesk-client-core/statuses/<sha>',
        {
            'description': 'waiting for start',
            'state': 'pending',
            'context': 'fire:www',
            'target_url': logs + '-sdcpr-1282/',
        }
    )
