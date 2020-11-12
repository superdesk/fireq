{{>build-init.sh}}

## clone cores
[ -d {{repo}}/server-core ] || (
mkdir -p {{repo}}
cd {{repo}}

github=git@github.com:superdesk
git clone $github/superdesk-core.git server-core
git clone $github/superdesk-client-core.git client-core
unset github
)

## server part
cd {{repo}}/server-core
time pip install -e .
time pip install -r requirements.txt

## client part
cd {{repo}}/client-core
time npm link
time grunt build --webpack-no-progress
