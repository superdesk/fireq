#!/bin/bash
# http://redsymbol.net/articles/unofficial-bash-strict-mode/
set -exuo pipefail
#IFS=$'\n\t'

export PATH=./node_modules/.bin/:$PATH
DEBIAN_FRONTEND=noninteractive
DBUS_SESSION_BUS_ADDRESS=/dev/null

_activate() {
    set +ux
    . {{repo_env}}/bin/activate
    set -ux
}

_skip_install() {
    dpkg -l | grep '^ii.*'$1 && [ -z "{{pkg_upgrade}}" ]
}
