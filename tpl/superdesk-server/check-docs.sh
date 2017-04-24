cd {{repo_server}}/docs
make html
[ ! -d {{repo_client}}/dist-deploy ] || cp -Tr _build/html {{repo_client}}/dist-deploy/docs
