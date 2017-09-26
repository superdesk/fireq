_activate
cd {{repo}}/server
if _missing_db; then
    ./manage.py app:initialize_data
    ./manage.py app:initialize_data -p {{repo}}/planning/server/data/
    ./manage.py users:create -u admin -p admin -e 'admin@example.com' --admin
else
    ./manage.py app:initialize_data
    ./manage.py app:initialize_data -p {{repo}}/planning/server/data/
fi
