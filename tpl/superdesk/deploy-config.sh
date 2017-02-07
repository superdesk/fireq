HOST=${HOST:-'{{host}}'}
HOST_SSL=${HOST_SSL:-'{{host_ssl}}'}

DB_HOST=${DB_HOST:-'{{db_host}}'}
DB_NAME=${DB_NAME:-'{{db_name}}'}

SUPERDESK_TESTING=${SUPERDESK_TESTING:-'{{testing}}'}
{{#dev}}
# keep using redis on localhost
REDIS_URL=redis://localhost:6379/1
{{/dev}}
