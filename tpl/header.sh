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
    curl -sI "$ELASTICSEARCH_URL/${ELASTICSEARCH_INDEX}_archive" | grep -q 404 && curl -sI $ELASTICSEARCH_URL/$ELASTICSEARCH_INDEX | grep -q 404
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

FIREQ_JSON=/opt/fireq.json

if [ ! -f $FIREQ_JSON ]; then
    echo '{}' > $FIREQ_JSON
fi

_merge_json_from_cwd() {
    # Merges the two fireq.json files
    # without overriding attributes already existing in
    # /opt/fireq.json
    if [ -f .fireq.json ]; then
        # Use a temporary file for the JSON destination
        # otherwise `jq` will override the file it's trying to read & write from/to
        mv $FIREQ_JSON $FIREQ_JSON.tmp
        jq -s '.[0] + .[1]' .fireq.json $FIREQ_JSON.tmp > $FIREQ_JSON
        rm $FIREQ_JSON.tmp
    fi
}

_merge_json_from_env_file() {
    if [ -f {{fireq_json}} ]; then
        pushd `dirname {{fireq_json}}`
        _merge_json_from_cwd
        popd
    fi
}

_get_json_value() {
    # Return the attribute name $1 from /opt/fireq.json
    # Falling back to $2 if provided
    # example: [ `_get_json_value elastic 2` -eq 7 ] && _ELASTIC_PORT=9201
    # example: if [ `_get_json_value sams` == "true" ]; then
    # example: BRANCH=`_get_json_value branch develop`
    if [ $# -eq 2 ] && [ `jq ".$1?" $FIREQ_JSON` == "null" ]; then
        echo $2
    else
        jq ".$1?" $FIREQ_JSON
    fi
}

_print_json_config() {1
    echo "FireQ JSON Config:"
    cat $FIREQ_JSON
}
