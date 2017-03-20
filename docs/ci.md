# [test.superdesk.org](https://test.superdesk.org)

**Authorization via Github, also people must be in [Superdesk Organisation][sd-people] to get access here.**

[sd-people]: https://github.com/orgs/superdesk/people

The main page contains the list of enabled repositories.

A repository page contains a list of **Pull Requests** and **Branches** with related links:
- `[instance]` link to the test instance
- `[deploy]` runs only deployment step
- `[restart]` runs failed/waiting steps if they are exist or runs all steps
- `[restart all]` runs all steps (including `build` step)
- `[reset db]` resets databases for the test instance

![A repository page](images/ci-repo-page.png)

## Test instance

**There are no real emails (by default),** all emails are stored in log files and can be found by url: `<domain>/mail`.

**Server logs** for particular instance can be found by url `<domain>/logs`.

For example for `sd-master`:
- https://sd-master.test.superdesk.org/mail/ emails
- https://sd-master.test.superdesk.org/logs/ logs

# Github integration

To enable a repository, a proper webhook should be installed
```
Payload URL: https://test.superdesk.org/hook
Secret: from /opt/fireq/config.js
```

After webhook is invoked by Github, `fireq` uses [Github API][gh-statuses] to post statuses.

[gh-statuses]: https://developer.github.com/v3/repos/statuses/

![Show all checks](images/gh-show-all-checks.png)
![Statuses](images/gh-checks.png)

## Minimal set of statuses
```
├─ fire:build       # build code for the proper git commit
├─ fire:www         # deploy the test instance, contains the link if successful
├─ fire:restart     # the way to restart failed (or all) steps from Github interface
```


