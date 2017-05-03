name='{{lxc_name}}'
ssh="{{ssh}} $name"

cat <<"EOF2" | $ssh
{{>header.sh}}

# previuos base container didn't have mongo/mongodump/mongorestore
# so keep this section for a while
if ! _skip_install mongodb-org-tools; then
pkg_upgrade=1
{{>add-mongo.sh}}
unset pkg_upgrade
fi

clean='{{clean}}'
backup='{{backup}}'
restore='{{restore}}'
mongo="mongo --quiet --host $DB_HOST"

backupdir=/var/tmp/data/backups
[ -d $backupdir ] || mkdir $backupdir

dbs() {
    cat <<EOF | $mongo
db.getMongo().getDBNames().forEach(function(v) {
    if (v.indexOf("${DB_NAME}_") === 0 || v == "$DB_NAME") {print(v)}
})
EOF
}

[ -z "$backup" ] || (
path=$backupdir/$backup
[ -d $path ] || mkdir $path
cd $path

for i in $(dbs); do
    sub="$(echo ${i}_main | cut -d'_' -f 2)"
    mongodump --host $DB_HOST -d $i -o .
    mv $i $sub
done
)

[ -z "$clean" ] || (
curl -s -XDELETE $DB_HOST:9200/$DB_NAME*
for i in $(dbs); do
     echo "db.dropDatabase()" | $mongo $i
done
)

[ -z "$restore" ] || (
systemctl stop {{name}}
_activate
cd {{repo}}/server

if curl -sI $ELASTICSEARCH_URL/$ELASTICSEARCH_INDEX | grep -q 404; then
    python manage.py app:initialize_data
fi

for i in $(dbs); do
    sub="$(echo ${i}_main | cut -d'_' -f 2)"
    mongorestore --host $DB_HOST -d $i --drop $backupdir/$restore/$sub
done

python manage.py app:index_from_mongo -f all --page-size 3000
systemctl start {{name}}
)
EOF2
