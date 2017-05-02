{{#names}}
DB_HOST={{db_host}}
DB_NAME={{.}}
{{>db-clean.sh}}
{{^only_dbs}}
lxc-destroy -fn {{.}} || true
{{/only_dbs}}
{{/names}}
