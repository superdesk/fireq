branch=planning-mvp
{{>superdesk/build-src-cores.sh}}

cd {{repo}}
sed -i 's/.*superdesk-planning.git.*/-e ..\/planning/' server/requirements.txt
sed -i -re 's/("superdesk-planning":)[^.]*(,?)/\1 "file:..\/planning"\2/' client/package.json
cat server/requirements.txt
cat client/package.json

repo={{repo}}/planning
{{>superdesk/build-src-repo.sh}}
