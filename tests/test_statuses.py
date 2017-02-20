from unittest.mock import patch

# patched in conftest.py:pytest_runtest_setup
logs = 'http://localhost/logs/all/20170101-000000-00'


@patch.dict('fireq.cli.conf', {'no_statuses': False})
@patch('fireq.gh.get_sha', lambda *a: '<sha>')
@patch('fireq.gh.clean_statuses', lambda *a: None)
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
    assert gh_call.call_count == 6
    a1, a2, a3, a4, a5, a6 = gh_call.call_args_list
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
            'description': 'click "Details" to restart the build',
            'target_url': 'http://localhost/sd/heads/master/restart',
            'context': 'fire:restart',
            'state': 'success'
        }
    )
    assert a3[0] == (
        'repos/superdesk/superdesk/statuses/<sha>',
        {
            'description': '',
            'target_url': logs + '-sd-master/build.log',
            'context': 'fire:build',
            'state': 'pending'
        }
    )
    assert a4[0] == (
        'repos/superdesk/superdesk/statuses/<sha>',
        {
            'description': 'duration: 0m0s',
            'target_url': logs + '-sd-master/build.log.htm',
            'context': 'fire:build',
            'state': 'success'
        }
    )
    assert a5[0] == (
        'repos/superdesk/superdesk/statuses/<sha>',
        {
            'description': '',
            'target_url': logs + '-sd-master/www.log',
            'context': 'fire:www',
            'state': 'pending'
        }
    )
    assert a6[0] == (
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
    assert gh_call.call_count == 4
    a1, a2, a3, a4 = gh_call.call_args_list
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
            'description': 'click "Details" to restart the build',
            'target_url': 'http://localhost/sd/heads/master/restart',
            'context': 'fire:restart',
            'state': 'success'
        }
    )
    assert a3[0] == (
        'repos/superdesk/superdesk/statuses/<sha>',
        {
            'description': '',
            'target_url': logs + '-sd-master/build.log',
            'context': 'fire:build',
            'state': 'pending'
        }
    )
    assert a4[0] == (
        'repos/superdesk/superdesk/statuses/<sha>',
        {
            'description': 'duration: 0m0s',
            'target_url': logs + '-sd-master/build.log.htm',
            'context': 'fire:build',
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


@patch('fireq.gh.get_sha', lambda *a: '<sha>')
def test_no_statuses(main, raises, capsys, gh_call):
    main('ci sd naspeh')
    assert not gh_call.called

    with patch.dict('fireq.cli.conf', {'no_statuses': False}):
        main('ci sd naspeh --dry-run')
        assert not gh_call.called


@patch.dict('fireq.cli.conf', {'no_statuses': False})
@patch('fireq.gh.get_sha', lambda *a: '<sha>')
def test_cleaning(gh_call, main, load_json):
    gh_call.return_value = load_json('status-sdcpr_1282.json')
    main('ci sdc pull/1282')

    s = [
        (i[0][1]['context'], i[0][1]['state'])
        for i in gh_call.call_args_list[1:]
    ]
    assert s == [
        ('fire:check-docs', 'success'),
        ('fire:check-e2e', 'success'),
        ('fire:!restart', 'success'),
        ('fire:check-e2e--part2', 'pending'),
        ('fire:restart', 'success'),
        ('fire:build', 'pending'),
        ('fire:build', 'success'),
        ('fire:check-e2e--part2', 'pending'),
        ('fire:check-e2e--part2', 'success')
    ]

    def call_args(context):
        return ('repos/superdesk/superdesk-client-core/statuses/<sha>', {
            'description': 'cleaned, is not presented anymore',
            'target_url': logs + '-sdcpr-1282/',
            'context': context,
            'state': 'success'
        })

    assert 10 == gh_call.call_count
    a1, a2, a3, a4, a5, a6, a7, a8, a9, a10 = gh_call.call_args_list
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
            'context': 'fire:check-e2e--part2',
            'target_url': logs + '-sdcpr-1282/',
        }
    )
    assert a6[0] == (
        'repos/superdesk/superdesk-client-core/statuses/<sha>',
        {
            'description': 'click "Details" to restart the build',
            'target_url': 'http://localhost/sdc/pull/1282/restart',
            'context': 'fire:restart',
            'state': 'success'
        }
    )
    assert a7[0] == (
        'repos/superdesk/superdesk-client-core/statuses/<sha>',
        {
            'description': '',
            'state': 'pending',
            'context': 'fire:build',
            'target_url': logs + '-sdcpr-1282/build.log',
        }
    )
    assert a8[0] == (
        'repos/superdesk/superdesk-client-core/statuses/<sha>',
        {
            'description': 'duration: 0m0s',
            'state': 'success',
            'context': 'fire:build',
            'target_url': logs + '-sdcpr-1282/build.log.htm',
        }
    )
    assert a9[0] == (
        'repos/superdesk/superdesk-client-core/statuses/<sha>',
        {
            'description': '',
            'state': 'pending',
            'context': 'fire:check-e2e--part2',
            'target_url': logs + '-sdcpr-1282/check-e2e--part2.log',
        }
    )
    assert a10[0] == (
        'repos/superdesk/superdesk-client-core/statuses/<sha>',
        {
            'description': 'duration: 0m0s',
            'state': 'success',
            'context': 'fire:check-e2e--part2',
            'target_url': logs + '-sdcpr-1282/check-e2e--part2.log.htm',
        }
    )

    # run all default targets
    gh_call.reset_mock()
    main('ci sdc pull/1282 --all')
    assert gh_call.call_count == 19
    s = [
        (i[0][1]['context'], i[0][1]['state'])
        for i in gh_call.call_args_list[1:]
    ]
    assert s[:9] == [
        # cleaned
        ('fire:check-docs', 'success'),
        ('fire:check-e2e', 'success'),
        ('fire:!restart', 'success'),
        # waiting statuses
        ('fire:www', 'pending'),
        ('fire:check-npmtest', 'pending'),
        ('fire:check-e2e--part1', 'pending'),
        ('fire:check-e2e--part2', 'pending'),

        ('fire:restart', 'success'),
        ('fire:build', 'pending'),
    ]
    assert set(s[9:]) == {
        ('fire:www', 'pending'),
        ('fire:check-npmtest', 'pending'),
        ('fire:check-e2e--part1', 'pending'),
        ('fire:check-e2e--part2', 'pending'),

        ('fire:build', 'success'),
        ('fire:www', 'success'),
        ('fire:check-npmtest', 'success'),
        ('fire:check-e2e--part1', 'success'),
        ('fire:check-e2e--part2', 'success'),
    }
