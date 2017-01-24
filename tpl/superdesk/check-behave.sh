cd {{repo_server}}
_activate

feature=(./features/*.feature)
[ -f $feature ] || exit 0


{{>add-dbs.sh}}


time behave --format progress2 --logging-clear-handlers --logcapture
