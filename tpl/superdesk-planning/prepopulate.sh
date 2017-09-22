_activate
cd {{repo}}/server
./manage.py app:initialize_data
./manage.py app:initialize_data -p {{repo}}/planning/server/data/
! _missing_db || ./manage.py users:create -u admin -p admin -e 'admin@example.com' --admin
