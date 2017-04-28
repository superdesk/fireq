{{#names}}
DB_HOST={{db_host}}
DB_NAME={{.}}
{{>db-clean.sh}}
lxc-destroy -fn {{.}} || true
{{/names}}
