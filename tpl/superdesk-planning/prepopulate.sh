_activate
cd {{repo}}/server
./manage.py app:initialize_data
./manage.py users:create -u admin -p admin -e 'admin@example.com' --admin
./manage.py app:initialize_data -p {{repo_core}}/server/data/
