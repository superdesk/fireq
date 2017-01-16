{{>superdesk/build-server.sh}}
[ ! -f dev-requirements.txt ] || time pip install -r dev-requirements.txt

cat <<EOF > /etc/profile.d/env.sh
. {{repo_env}}/bin/activate
EOF
