db_host="{{db_host}}"
db_name="{{uid}}"
{{>db-clean.sh}}

{{>ci-deploy.sh}}
