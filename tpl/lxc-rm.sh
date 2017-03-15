{{#names}}
db_host={{db_host}}
db_name={{.}}
{{>db-clean.sh}}
lxc-destroy -fn {{.}} || true
{{/names}}
