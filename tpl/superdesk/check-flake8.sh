cd {{repo_server}}
_activate

# run flake8 with one job, because it could lock the build for ever
flake8 --jobs=1
