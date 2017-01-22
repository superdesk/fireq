from unittest.mock import patch

# patched in conftest.py:pytest_runtest_setup
logs = 'http://localhost/logs/all/20170101-000000-00'


@patch('firelib.gh.get_sha')
@patch('firelib.gh.call')
def test_base(_call, _sha, sp, main, raises):
    _call.return_value = {}
    _sha.return_value = '<sha>'

    main('ci sds master -t build')
    assert _call.call_count == 3
    a1, a2, a3 = _call.call_args_list
    assert a1[0] == (
        'repos/superdesk/superdesk-core/statuses/<sha>',
        {
            'description': 'Click "Details" to restart the build',
            'target_url': 'http://localhost/sds/heads/master/restart',
            'context': 'fire:!restart',
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
            'description': '',
            'target_url': logs + '-sds-master/build.log.htm',
            'context': 'fire:build',
            'state': 'success'
        }
    )

    _call.reset_mock()
    main('ci sd master -t www')
    assert _call.call_count == 2
    a1, a2 = _call.call_args_list
    assert a1[0] == (
        'repos/superdesk/superdesk/statuses/<sha>',
        {
            'description': '',
            'target_url': logs + '-sd-master/www.log',
            'context': 'fire:www',
            'state': 'pending'
        }
    )
    assert a2[0] == (
        'repos/superdesk/superdesk/statuses/<sha>',
        {
            'description': 'Click "Details" to see the test instance',
            'target_url': 'http://sd-master.localhost',
            'context': 'fire:www',
            'state': 'success'
        }
    )

    _call.reset_mock()
    sp.call.return_value = 16
    with raises(SystemExit):
        main('ci sd master -t www')
    assert _call.call_count == 2
    a1, a2 = _call.call_args_list
    assert a1[0] == (
        'repos/superdesk/superdesk/statuses/<sha>',
        {
            'description': '',
            'target_url': logs + '-sd-master/www.log',
            'context': 'fire:www',
            'state': 'pending'
        }
    )
    assert a2[0] == (
        'repos/superdesk/superdesk/statuses/<sha>',
        {
            'description': '',
            'target_url': logs + '-sd-master/www.log.htm',
            'context': 'fire:www',
            'state': 'failure'
        }
    )

    # should be all pending statuses in the begining
    _call.reset_mock()
    sp.call.return_value = 0
    main('ci sd master')
    assert _call.call_count == 9
    s = [(i[0][1]['context'], i[0][1]['state']) for i in _call.call_args_list]
    assert s[:5] == [
        ('fire:!restart', 'success'),

        ('fire:build', 'pending'),
        ('fire:www', 'pending'),
        ('fire:check-npmtest', 'pending'),
        ('fire:check-flake8', 'pending'),
    ]
    assert set(s[5:]) == {
        ('fire:build', 'success'),
        ('fire:www', 'success'),
        ('fire:check-npmtest', 'success'),
        ('fire:check-flake8', 'success'),
    }


def test_base__real_http(sp, capfd, real_http, main):
    main('ci sd naspeh')
    out, err = capfd.readouterr()
    assert 9 == err.count("201 url='https://api.github.com/repos/")
