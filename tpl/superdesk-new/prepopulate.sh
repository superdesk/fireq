_activate
cd {{repo}}
python manage.py app:prepopulate
python manage.py users:create -u admin -p admin -e 'admin@example.com' --admin
