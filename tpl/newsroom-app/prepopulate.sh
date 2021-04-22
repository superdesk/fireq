_activate

cd {{repo}}/server
python manage.py initialize_data
python manage.py data_upgrade
python manage.py create_user admin@example.com admin Admin Admin true || :
