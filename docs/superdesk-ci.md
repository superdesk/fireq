# [test.superdesk.org][1]

**It uses authorization via Github, also people must be in [Superdesk Organisation][2] to get access here.**

From the dashboard (needs UI improvements and more information).:
- builds can be restarted
- links to the test instances can be found

Logs can be found here: https://test.superdesk.org/logs/

# Fire:build

During the build there are many statuses posted via [Github API][3].

For example: the list for [superdesk-client-core][4] (click on green tick):
```
├─ fire:!restart
├─ fire:build
├─ fire:check-docs
├─ fire:check-e2e
├─ fire:check-e2e--part1
├─ fire:check-e2e--part2
├─ fire:check-npmtest
├─ fire:www
```
- `fire:!restart` is just status for restarting the build from github interface
- `fire:www` if successful has link to test instance for particular PR or branch

# Fire:www

A test instance is separate LXC container with proper changes for each PR or branch.
- it is pre-populated with data (it uses data for e2e tests now with some modifications)
- **there are no real emails,** all emails are stored as logs and can be found by url: `<domain>/mail` (for example: https://sd-master.test.superdesk.org/mail)


[1]: https://test.superdesk.org
[2]: https://github.com/orgs/superdesk/people
[3]: https://developer.github.com/v3/repos/statuses/
[4]: https://github.com/superdesk/superdesk-client-core/branches

