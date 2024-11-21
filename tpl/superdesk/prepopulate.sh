### prepopulate
_activate
cd {{repo}}/server

python manage.py app:initialize_data
python manage.py users:create -u admin -p admin -e 'admin@example.com' --admin
python manage.py data:upgrade
python manage.py schema:migrate || true

# If SAMS is enabled in fireq.json, initialise elasticsearch
# Deletes elastic indices, recreate the types/mapping, then reindex from mongo
if [ `_get_json_value sams` == "true" ]; then
    # Use pushd/popd so we can return to the current working directory
    # Change directory to where the sams `settings.py` file resides
    pushd {{repo}}/server/sams
    python -m sams.manage app:flush_elastic_index
    popd
fi