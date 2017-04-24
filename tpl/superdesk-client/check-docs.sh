# TODO: these docs are not working anymore, so it's not used for now
cd {{repo_client}}
[ -z "$(grep no-serve tasks/options/dgeni-alive.js)" ] || grunt docs --no-serve
