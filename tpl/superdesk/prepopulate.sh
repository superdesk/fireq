### prepopulate
_activate
cd {{repo}}/server

_sample_data() {
    [ -z "${sample_data:-}" ] || sample_data='--sample-data'
    python manage.py app:initialize_data --help | grep -- --sample-data && sample_data= || sample_data=$sample_data
}

{{^test_data}}
_sample_data
python manage.py app:initialize_data $sample_data
python manage.py users:create -u admin -p admin -e 'admin@example.com' --admin
{{/test_data}}
{{#test_data}}
if curl -sI {{db_host}}:9200/{{db_name}} | grep -q 404; then
    _sample_data
    # add default vocabularies
    ./manage.py app:initialize_data --entity-name vocabularies
    # add Forbes ingest source
    ./manage.py app:initialize_data --entity-name ingest_providers $sample_data
    # Use data from e2e tests
    ./manage.py app:prepopulate
fi
{{/test_data}}
unset sample_data
