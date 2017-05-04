{{#names}}
./fire lxc-db -c {{.}}
lxc-destroy -fn {{.}} || true
{{/names}}
