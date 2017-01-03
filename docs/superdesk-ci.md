# Fire:build

During the build there are many statuses posted via [Github API][1].

For example: the tree for [superdesk-client-core][2]:
```
├─ fire:!restart
├─ fire:build
│   ├─ fire:check-docs
│   ├─ fire:check-e2e
│   ├─ fire:check-npmtest
│   ├─ fire:www
```
- `fire:!restart` is just status for restarting the build from github interface.
- `fire:build` is root status, if some of his children are failing it's also failing.
- `fire:www` if successful has link to test instance for particular PR or branch.

# [test.superdesk.org][3]

This is simple dashboard (needs UI improvements and more information).

**It uses authorization via Github, also people must be in [Superdesk Organisation][4] to get access here.**

From this dashboard:
- builds can be restarted
- links to test instances can be found

# Fire:www

A test instance is separate LXC container with proper changes for each PR or branch.
- it is pre-populated with data (it uses data for e2e tests now with some modifications)
- **there are no real emails,** all emails are stored as logs and can be found by url: `<domain>/mail` (for example: https://sd-master.test.superdesk.org/mail)


[1]: https://developer.github.com/v3/repos/statuses/
[2]: https://github.com/superdesk/superdesk-client-core/pulls
[3]: https://test.superdesk.org
[4]: https://github.com/orgs/superdesk/people

