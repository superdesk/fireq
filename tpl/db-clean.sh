curl -s -XDELETE $db_host:9200/$db_name*
cat <<EOF | mongo --host $db_host --quiet
db.getMongo().getDBNames().forEach(function(v) {
    if (v.indexOf("$db_name") === 0) {
        db.getSiblingDB(v).dropDatabase()
    }
})
EOF
# mongo="mongo --host $db_host --quiet"
# echo "db.dropDatabase()" | $mongo $db_name
# echo "db.dropDatabase()" | $mongo ${db_name}_ar
# echo "db.dropDatabase()" | $mongo ${db_name}_la
# echo "db.dropDatabase()" | $mongo ${db_name}_ca
