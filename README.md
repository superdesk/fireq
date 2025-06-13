Fireq has Github integration and  can deploy, run predefined CI checks (like `flake8`, `nosetests` e2e tests, etc.), backup databases for according instance, generate base containers, etc. [More details.](docs/ci.md)

Fireq is built around command line interface `./fire -h`, it uses [mustache][mustache] templates in `tpl` directory to generate straightforward bash scripts. Mustache gives ability to use includes and override just few files as needed, for example the main directory is [tpl/superdesk](https://github.com/superdesk/fireq/tree/master/tpl/superdesk) and it contains a lot of files, but to adjust Liveblog deployment it needs override [few of them](https://github.com/superdesk/fireq/tree/master/tpl/liveblog) so no duplication needed. It proved already that it's pretty flexible and works pretty well.

[mustache]: https://mustache.github.io/mustache.5.html

Fireq uses [LXC](docs/lxc.md) for CI and deployment.

Web application is built with [aiohttp](http://aiohttp.readthedocs.io) and it's wrapper around `fireq.cli` and handles Github webhooks and CI Dashbord.

Repository contains tree main branches:
1. `master` with code
2. `init` files to override behavior of according instance ([details](docs/ci.md#init))
3. `files` is separate branch for auto-generated install files

# Installations
- [Superdesk for users](https://github.com/superdesk/fireq/tree/files/superdesk)
- [Superdesk for developers](https://github.com/superdesk/fireq/tree/files/superdesk#development)
- [Liveblog for users](https://github.com/superdesk/fireq/tree/files/liveblog)
- [Liveblog for developers](https://github.com/superdesk/fireq/tree/files/liveblog#development)

## Generate files
To test install scripts:
```sh
./fire gen-files

# superdesk
./fire lxc-init sd
cat files/superdesk/install | ./fire lxc-ssh sd
```

## History
Details in according issue: [SDESK-146](https://sofab.atlassian.net/browse/SDESK-146).
