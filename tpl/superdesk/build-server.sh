### Server part
# init virtualenv
env={{repo_env}}
[ -d $env ] && rm -rf $env
python3 -m venv $env
unset env

_activate
pip install -U pip wheel

cd {{repo_server}}
time pip install -U -r requirements.txt
