{{>add-dbs.sh}}
{{>testing.sh}}

cd {{repo_server}}
_activate

time nosetests -v --with-id
