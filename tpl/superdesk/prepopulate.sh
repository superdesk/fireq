### prepopulate
_activate
cd {{repo}}/server

_sample_data() {
    sample_data=${sample_data:-}
    [ -z "$sample_data" ] || sample_data='--sample-data'
    (python manage.py app:initialize_data --help | grep -- --sample-data) && sample_data=$sample_data || sample_data=
}

{{^test_data}}
if curl -sI $ELASTICSEARCH_URL/$ELASTICSEARCH_INDEX | grep -q 404; then
    _sample_data
    python manage.py app:initialize_data $sample_data
    python manage.py users:create -u admin -p admin -e 'admin@example.com' --admin
else
    python manage.py app:initialize_data
fi
{{/test_data}}
{{#test_data}}
if curl -sI $ELASTICSEARCH_URL/$ELASTICSEARCH_INDEX | grep -q 404; then
    _sample_data
    # add default vocabularies
    python manage.py app:initialize_data --entity-name vocabularies
    # add default validators
    python manage.py app:initialize_data --entity-name validators
    # add Forbes ingest source
    python manage.py app:initialize_data --entity-name ingest_providers $sample_data
    # Use data from e2e tests
    python manage.py app:prepopulate
else
    python manage.py app:initialize_data
fi
{{/test_data}}
unset sample_data
