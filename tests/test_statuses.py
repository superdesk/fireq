import datetime as dt
from unittest.mock import patch

from fire import run_jobs

now = dt.datetime(2017, 1, 1)
randint = 0
logs = 'http://localhost/logs/all/20170101-000000-00'


@patch('fire.random')
@patch('fire.dt.datetime')
@patch('fire.subprocess')
@patch('fire.gh.get_sha')
@patch('fire.gh.call')
def test_base(_call, _sha, _sp, _dt, _rand):
    _rand.randint.return_value = 0
    _dt.now.return_value = now
    _sp.call.return_value = 0
    _call.return_value = {}
    _sha.return_value = '<sha>'

    run_jobs(['build'], 'sds')
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
            'target_url': logs + '-sds-master/build.log',
            'context': 'fire:build',
            'state': 'success'
        }
    )

    _call.reset_mock()
    run_jobs(['www'])
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
    _sp.call.return_value = 16
    run_jobs(['www'])
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
            'target_url': logs + '-sd-master/www.log',
            'context': 'fire:www',
            'state': 'failure'
        }
    )

    # should be all pending statuses in the begining
    _call.reset_mock()
    _sp.call.return_value = 0
    run_jobs()
    assert _call.call_count == 13
    s = [(i[0][1]['context'], i[0][1]['state']) for i in _call.call_args_list]
    assert s[:7] == [
        ('fire:!restart', 'success'),

        ('fire:build', 'pending'),
        ('fire:www', 'pending'),
        ('fire:check-npmtest', 'pending'),
        ('fire:check-flake8', 'pending'),
        ('fire:check-nose', 'pending'),
        ('fire:check-behave', 'pending'),
    ]
    assert set(s[7:]) == {
        ('fire:build', 'success'),
        ('fire:www', 'success'),
        ('fire:check-npmtest', 'success'),
        ('fire:check-flake8', 'success'),
        ('fire:check-nose', 'success'),
        ('fire:check-behave', 'success'),
    }


@patch('fire.subprocess')
def test_base__real_http(_sp, real_http):
    _sp.call.return_value = 0
    run_jobs(ref_name='naspeh')
