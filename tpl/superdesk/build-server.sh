## server part
# init virtualenv
env={{repo_env}}
[ -d $env ] && rm -rf $env
python3 -m venv $env
echo 'export PATH=./node_modules/.bin/:$PATH' >> $env/bin/activate
unset env

_activate
pip install -U pip wheel

cd {{repo_server}}
time pip install -U -r requirements.txt
{{#dev}}
[ ! -f dev-requirements.txt ] || time pip install -r dev-requirements.txt

cat <<EOF > /etc/profile.d/env.sh
. {{repo_env}}/bin/activate
EOF
{{/dev}}
