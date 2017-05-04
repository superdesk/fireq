{{#names}}
./fire lxc-db -c {{.}} || ./fire lxc-db -c --db-name={{.}} {{db_host}}
lxc-destroy -fn {{.}} || true
{{/names}}
