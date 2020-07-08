### init && upgrade
_activate
cd {{repo}}/server

{{^test_data}}
if _missing_db; then
    python manage.py app:initialize_data
    python manage.py users:create -u admin -p admin -e 'admin@example.com' --admin
else
    python manage.py app:initialize_data
    python manage.py data:upgrade
fi
{{/test_data}}
