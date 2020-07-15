{{#sams_enabled}}
## clone SAMS repo
[ -d {{repo}}/sams ] || (
mkdir -p {{repo}}
cd {{repo}}

github=https://github.com/superdesk
git clone $github/sams.git sams
unset github
)

## server part
cd {{repo}}/sams/src/server
time pip install -e .

## client part
cd {{repo}}/sams/src/clients/python
time pip install -e .
{{/sams_enabled}}
