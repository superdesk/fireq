### prepopulate
_activate
cd {{repo}}/server
if curl -sI $ELASTICSEARCH_URL/$ELASTICSEARCH_INDEX | grep -q 404; then
    python manage.py app:initialize_data

    # for master it should be '--admin=true' for devel just '--admin'
    python manage.py users:create --help | grep -- '-a ADMIN' && admin='--admin=true' || admin='--admin'
    python manage.py users:create -u admin -p admin -e 'admin@example.com' $admin

    python manage.py register_local_themes
else
    python manage.py app:initialize_data
    python manage.py register_local_themes
fi
