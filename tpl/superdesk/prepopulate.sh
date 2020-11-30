### prepopulate
_activate
cd {{repo}}/server

_sample_data() {
    sample_data=${sample_data:-}
    [ -z "$sample_data" ] || sample_data='--sample-data'
    (python manage.py app:initialize_data --help | grep -- --sample-data) && sample_data=$sample_data || sample_data=
}

{{^test_data}}
if _missing_db; then
    _sample_data
    python manage.py app:initialize_data $sample_data
    python manage.py users:create -u admin -p admin -e 'admin@example.com' --admin
else
    python manage.py data:upgrade
    python manage.py schema:migrate || :
    python manage.py app:initialize_data
    python manage.py users:create -u admin -p admin -e 'admin@example.com' --admin
fi
{{/test_data}}
{{#test_data}}
if _missing_db; then
    _sample_data
    # add default vocabularies
    python manage.py app:initialize_data --entity-name vocabularies
    # add default validators
    python manage.py app:initialize_data --entity-name validators
    # add Forbes ingest source
    python manage.py app:initialize_data --entity-name ingest_providers $sample_data
    # Use data from e2e tests
    python manage.py app:prepopulate || :
else
    python manage.py data:upgrade
    python manage.py app:initialize_data
fi
{{/test_data}}

# If SAMS is enabled in fireq.json, initialise elasticsearch
# Deletes elastic indices, recreate the types/mapping, then reindex from mongo
if [ -f {{fireq_json}} ] && [ `jq ".sams?" {{fireq_json}}` == "true" ]; then
    # Use pushd/popd so we can return to the current working directory
    # Change directory to where the sams `settings.py` file resides
    pushd {{repo}}/server/sams
    python -m sams.manage app:flush_elastic_index
    popd
fi

unset sample_data
