#!/bin/bash
# http://redsymbol.net/articles/unofficial-bash-strict-mode/
set -exuo pipefail

export DEBIAN_FRONTEND=noninteractive
export DBUS_SESSION_BUS_ADDRESS=/dev/null

_activate() {
    set +ux
    . {{activate}}
    set -ux
}

_missing_db() {
    ! { curl -sI "$ELASTICSEARCH_URL/${ELASTICSEARCH_INDEX}_archive" | grep -q 404 && curl -sI $ELASTICSEARCH_URL/$ELASTICSEARCH_INDEX | grep -q 404 ;}
}

_skip_install() {
    dpkg -l | grep '^ii.*'$1 && [ -z ${pkg_upgrade:-'{{pkg_upgrade}}'} ]
}

_set_config() {
    # Adds the line ($1) to the config file
    # example: _set_config "superdesk_branch=`jq -r ".superdesk_branch?" .fireq.json`"
    echo "$1" >> /opt/fireq.config
}

_get_config() {
    # Gets the config line
    # example: if _get_config "sams=1"; then
    [ -f /opt/fireq.config ] && grep -Fxq "$1" /opt/fireq.config
}

_get_config_value() {
    # Gets the config value of $1, separated by a '=' character
    # Returns $2 if not found (optional)
    # example: branch=`_get_config_value superdesk_branch ${branch:-master}`
    if [ ! -f /opt/fireq.config ] || ! grep -Fq "$1=" /opt/fireq.config; then
        echo $2
    else
        grep -F "$1" /opt/fireq.config | awk -F= '{print $2}'
    fi
}
