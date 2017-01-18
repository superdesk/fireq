### prepopulate
_activate
cd {{repo}}/server
[ -z "${sample_data:-1}" ] || sample_data='--sample-data'
python manage.py app:initialize_data --help | grep -- --sample-data && sample_data=$sample_data || sample_data=

python manage.py app:initialize_data $sample_data
python manage.py users:create -u admin -p admin -e 'admin@example.com' --admin
