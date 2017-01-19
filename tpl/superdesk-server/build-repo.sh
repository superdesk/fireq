repo={{repo}}
github=https://github.com/superdesk
# rm -rf $repo
if [ ! -d $repo ]; then
    mkdir $repo
    cd $repo
    git init
    git remote add origin $github/superdesk.git

    git fetch origin master
    git checkout origin/master
    sed -i 's/.*superdesk-core.git.*/-e ..\/server-core/' server/requirements.txt
    sed -i -re 's/("superdesk-core":).*/\1 "file:..\/client-core"/' client/package.json

    git submodule add -b master $github/superdesk-core.git server-core
    git submodule add -b master $github/superdesk-client-core.git client-core
fi
unset repo github

{{>superdesk/build-repo.sh}}
