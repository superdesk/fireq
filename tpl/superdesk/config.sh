# put your variables here!
HOST=${host:-'{{host}}'}
HOST_SSL=${host_ssl:-'{{host_ssl}}'}

DB_HOST=${db_host:-'{{db_host}}'}
DB_NAME=${db_name:-'{{db_name}}'}

# keep using redis on localhost
REDIS_URL=redis://localhost:6379/1

SUPERDESK_TESTING=${testing:-'{{testing}}'}

# use elastic based on superdesk-core config
ELASTIC_PORT=9200
[ -f {{repo_server}}/.fireq.json ] && [ `jq ".elastic?" {{repo_server}}/.fireq.json` -eq 7 ] && ELASTIC_PORT=9201
