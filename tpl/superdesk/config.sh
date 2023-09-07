# put your variables here!
HOST=${host:-'{{host}}'}
HOST_SSL=${host_ssl:-'{{host_ssl}}'}
CLIENT_URL=https://${host:-'{{host}}'}

DB_HOST=${db_host:-'{{db_host}}'}
DB_NAME=${db_name:-'{{db_name}}'}

# keep using redis on localhost
REDIS_URL=redis://localhost:6379/1

SUPERDESK_TESTING=${testing:-'{{testing}}'}
