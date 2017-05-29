repo={{repo}}
github=https://github.com/superdesk
[ -d $repo ] || mkdir $repo
cd $repo
if [ ! -d $repo/.git ]; then
    git init
    git remote add origin $github/superdesk.git

    git fetch origin planning-mvp
    git checkout planning-mvp

    sed -i 's/.*superdesk-planning.git.*/-e ..\/planning/' server/requirements.txt
    cat server/requirements.txt

    sed -i -re 's/("superdesk-planning":).*/\1 "file:..\/planning",/' client/package.json
    cat client/package.json
fi
unset repo github

repo={{repo}}/planning
{{>superdesk/build-src-repo.sh}}
