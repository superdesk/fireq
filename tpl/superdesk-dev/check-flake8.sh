cd {{repo_server}}
_activate

# run flake8 with on jobs, because it could lock the build for ever
flake8 --jobs=1
