{{>superdesk/build-src-cores.sh}}

cd {{repo}}
sed -i 's/.*superdesk-analytics.git.*/-e ..\/analytics/' server/requirements.txt
sed -i -re 's/("superdesk-analytics":)[^,]*(,?)/\1 "file:..\/analytics"\2/' client/package.json
cat server/requirements.txt
cat client/package.json

repo={{repo}}/analytics
{{>superdesk/build-src-repo.sh}}
