### prepopulate
_activate
cd {{repo}}/server
if _missing_db; then
    python manage.py app:initialize_data

    # for master it should be '--admin=true' for devel just '--admin'
    python manage.py users:create --help | grep -- '-a ADMIN' && admin='--admin=true' || admin='--admin'
    python manage.py users:create -u admin -p admin -e 'admin@example.com' $admin

else
    python manage.py app:initialize_data
fi

# fix 'IndexMissingException[[lb-*] missing]' errors
curl -s -XPUT $ELASTICSEARCH_URL/$ELASTICSEARCH_INDEX

python manage.py register_local_themes
python manage.py register_bloglist
