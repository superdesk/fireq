#!/bin/bash
{{{header_doc}}}
# http://redsymbol.net/articles/unofficial-bash-strict-mode/
set -exuo pipefail
# IFS=$'\n\t'

DEBIAN_FRONTEND=noninteractive
DBUS_SESSION_BUS_ADDRESS=/dev/null

_activate() {
    set +ux
    . {{repo_env}}/bin/activate
    set -ux
}

_skip_install() {
    dpkg -l | grep '^ii.*'$1 && [ -z ${pkg_upgrade:-'{{pkg_upgrade}}'} ]
}
