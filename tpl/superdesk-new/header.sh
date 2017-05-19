#!/bin/bash
{{{header_doc}}}
# http://redsymbol.net/articles/unofficial-bash-strict-mode/
set -exuo pipefail

export DEBIAN_FRONTEND=noninteractive
export DBUS_SESSION_BUS_ADDRESS=/dev/null

_activate() {
    set +ux
    if [ -f {{repo}}/activate ]; then
        . {{repo}}/activate
    else
        . {{repo_env}}/bin/activate
    fi
    set -ux
}

_skip_install() {
    dpkg -l | grep '^ii.*'$1 && [ -z ${pkg_upgrade:-'{{pkg_upgrade}}'} ]
}
