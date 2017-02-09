{{#names}}
lxc-destroy -fn {{.}} || true
curl -q -XDELETE {{db_host}}:9200/{{.}}*
cat <<EOF | mongo --host {{db_host}} --quiet
db.getMongo().getDBNames().forEach(function(v) {
    if (v.indexOf("{{.}}") === 0) {
        db.getSiblingDB(v).dropDatabase()
    }
})
EOF
# mongo="mongo --host {{db_host}} --quiet"
# echo "db.dropDatabase()" | $mongo {{.}}
# echo "db.dropDatabase()" | $mongo {{.}}_ar
# echo "db.dropDatabase()" | $mongo {{.}}_la
# echo "db.dropDatabase()" | $mongo {{.}}_ca
{{/names}}
