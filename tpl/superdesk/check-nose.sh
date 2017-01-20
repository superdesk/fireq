{{>add-dbs.sh}}


cd {{repo_server}}
_activate

time nosetests -v --with-id
