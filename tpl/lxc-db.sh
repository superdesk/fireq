# previuos base container didn't have mongo/mongodump/mongorestore
# so keep this section for a while
if ! _skip_install mongodb-org-tools; then
pkg_upgrade=1
{{>add-mongo.sh}}
unset pkg_upgrade
fi

{{#db_name}}
db_name='{{db_name}}'
db_host='{{lxc_name}}'
{{/db_name}}
{{^db_name}}
[ -f {{activate}} ] || (
    echo '. {{repo_env}}/bin/activate' > {{activate}}
)
_activate
db_name=$DB_NAME
db_host=$DB_HOST
{{/db_name}}
clean='{{clean}}'
backup='{{backup}}'
restore='{{restore}}'
mongo="mongo --quiet --host $db_host"

backupdir=/var/tmp/data/backups
[ -d $backupdir ] || mkdir -p $backupdir

dbs() {
    cat <<EOF | $mongo
db.getMongo().getDBNames().forEach(function(v) {
    if (v.indexOf("${db_name}_") === 0 || v == "$db_name") {print(v)}
})
EOF
}

[ -z "$backup" ] || (
[ "$backup" != "-" ] || backup="$db_host/$(date +%Y%m%d%H%M%S)--$db_name"
path=$backupdir/$backup
[ -d $path ] || mkdir -p $path
cd $path

for i in $(dbs); do
    sub="$(echo ${i}_main | cut -d'_' -f 2)"
    mongodump --host $db_host -d $i -o .
    mv $i $sub
done
echo "Done: $backup"
)

[ -z "$clean" ] || (
curl -s -XDELETE $db_host:9200/$db_name*
curl -s -XDELETE $db_host:9201/$db_name*
for i in $(dbs); do
     echo "db.dropDatabase()" | $mongo $i
done
)

[ -z "$restore" ] || (
systemctl stop {{name}}
cd {{repo}}/server

if _missing_db; then
    python manage.py app:initialize_data
fi

for i in $(dbs); do
    sub="$(echo ${i}_main | cut -d'_' -f 2)"
    mongorestore --host $db_host -d $i --drop $backupdir/$restore/$sub
done

cmd='python manage.py app:index_from_mongo --page-size 3000'
$cmd --all || (
    $cmd -f ingest
    $cmd -f published
    $cmd -f items
    $cmd -f archive
    $cmd -f archived
)

systemctl start {{name}}
)
