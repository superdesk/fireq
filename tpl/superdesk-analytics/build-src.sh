repo={{repo}}
github=https://github.com/superdesk
[ -d $repo ] || mkdir $repo
cd $repo
if [ ! -d $repo/.git ]; then
    git init
    git remote add origin $github/superdesk.git

    git fetch origin master
    git checkout 1684cecb6c1b9f5c67d7f7b291e4cbf4378808fc

    sed -i 's/.*superdesk-analytics.git.*/-e ..\/analytics/' server/requirements.txt
    cat server/requirements.txt

    sed -i -re 's/("superdesk-analytics":).*/\1 "file:..\/analytics",/' client/package.json
    cat client/package.json
fi
unset repo github

repo={{repo}}/analytics
{{>superdesk/build-src-repo.sh}}
