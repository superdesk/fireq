curl -s -XDELETE $DB_HOST:9200/$DB_NAME*
cat <<EOF | mongo --host $DB_HOST --quiet
db.getMongo().getDBNames().forEach(function(v) {
    if (v.indexOf("$DB_NAME") === 0) {
        db.getSiblingDB(v).dropDatabase()
    }
})
EOF
# mongo="mongo --host $DB_HOST --quiet"
# echo "db.dropDatabase()" | $mongo $DB_NAME
# echo "db.dropDatabase()" | $mongo ${DB_NAME}_ar
# echo "db.dropDatabase()" | $mongo ${DB_NAME}_la
# echo "db.dropDatabase()" | $mongo ${DB_NAME}_ca
