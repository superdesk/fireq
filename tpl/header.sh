#!/bin/bash
# http://redsymbol.net/articles/unofficial-bash-strict-mode/
set -exuo pipefail
IFS=$'\n\t'

export DEBIAN_FRONTEND=noninteractive
export DBUS_SESSION_BUS_ADDRESS=/dev/null
export PATH=./node_modules/.bin/:$PATH

_activate() {
    set +ux
    . {{repo_env}}/bin/activate
    set -ux
}
