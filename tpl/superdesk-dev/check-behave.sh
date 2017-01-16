cd {{repo_server}}
_activate

[ ! -f ./features/*.feature ] || time behave --format progress2 --logging-clear-handlers --logcapture
