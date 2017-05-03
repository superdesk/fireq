{{#names}}
./fire db -c {{.}}
lxc-destroy -fn {{.}} || true
{{/names}}
