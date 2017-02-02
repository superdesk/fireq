Replace `<you_ip_or_domain>` with domain where Superdesk will be accessible.
For example `test.superdesk.org` or `139.59.154.138`

## Install a Superdesk on fresh Ubuntu 16.04
```sh
(echo HOST=<you_ip_or_domain>; curl https://raw.githubusercontent.com/naspeh-sf/deploy/master/files/superdesk/install) | sudo bash
```

## Install a Liveblog on fresh Ubuntu 16.04
```sh
(echo HOST=<you_ip_or_domain>; curl https://raw.githubusercontent.com/naspeh-sf/deploy/master/files/liveblog/install) | sudo bash
```
