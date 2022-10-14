{{#names}}
./fire lxc-db -c {{.}} || ./fire lxc-db -c --db-name={{.}} {{db_host}}
lxc delete -f {{.}} || true
{{/names}}
