repo={{repo}}
github=https://github.com/superdesk
# rm -rf $repo
if [ ! -d $repo ]; then
    mkdir $repo
    cd $repo
    git init
    git remote add origin $github/superdesk.git

    git fetch origin planning-mvp
    git checkout planning-mvp

    sed -i 's/.*superdesk-planning.git.*/-e ..\/planning/' server/requirements.txt
    cat server/requirements.txt

    sed -i -re 's/("superdesk-planning":).*/\1 "file:..\/planning",/' client/package.json
    cat client/package.json

    git submodule add -b master $github/superdesk-planning.git planning
fi
unset repo github

{{>superdesk/build-repo.sh}}
