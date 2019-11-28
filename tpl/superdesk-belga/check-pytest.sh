{{>add-dbs.sh}}
{{>testing.sh}}

cd {{prod_api_path}}
_activate

time pytest
