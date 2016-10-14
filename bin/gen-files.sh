#!/bin/sh
set -e

root=$(dirname $(dirname $(realpath -s $0)))
path=$root/files

[ -d $path ] || mkdir $path

# superdesk
endpoint=superdesk/master
. $root/bin/install.tpl > $path/superdesk.sh

endpoint=superdesk/10
. $root/bin/install.tpl > $path/superdesk-10.sh

# liveblog
endpoint=liveblog/master
. $root/bin/install.tpl > $path/liveblog.sh

chmod +x $path/*
