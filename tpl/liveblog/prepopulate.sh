### prepopulate
_activate

unset ELASTIC_PORT
unset _ELASTIC_PORT
cd {{repo}}/server
if _missing_db; then
    [ -f app_init_elastic.py ] && python app_init_elastic.py
    python manage.py app:initialize_data

    # for master it should be '--admin=true' for devel just '--admin'
    python manage.py users:create --help | grep -- '-a ADMIN' && admin='--admin=true' || admin='--admin'
    python manage.py users:create -u admin -p admin -fn Admin -ln Admin -e 'admin@example.com' $admin

else
    python manage.py app:initialize_data
fi

# fix 'IndexMissingException[[lb-*] missing]' errors
curl -s -XPUT $ELASTICSEARCH_URL/$ELASTICSEARCH_INDEX

python manage.py register_local_themes
python manage.py register_bloglist

# Multi-tenant branches: `users:create` above knows nothing about tenants, so the
# admin cannot see any tenant-scoped resource until it belongs to one. The migration
# command assigns everything without a tenant to a single one; no-op on later runs.
if python manage.py liveblog:migrate_tenancy --help > /dev/null 2>&1; then
    python manage.py liveblog:migrate_tenancy --tenant-name "Fireq"
fi
