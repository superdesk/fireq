#!/bin/sh
set -e

path=files

[ -d $path ] || mkdir $path

# superdesk
endpoint=superdesk/master
. bin/install.tpl > $path/superdesk.sh

endpoint=superdesk/10
. bin/install.tpl > $path/superdesk-10.sh

# liveblog
endpoint=liveblog/master
. bin/install.tpl > $path/liveblog.sh

chmod +x $path/*
