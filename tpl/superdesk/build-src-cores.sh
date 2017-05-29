repo={{repo}}
github=https://github.com/superdesk
branch=${branch:-master}

[ -d $repo ] || mkdir $repo
cd $repo
if [ ! -d $repo/.git ]; then
    git init
    git remote add origin $github/superdesk.git

    git fetch origin $branch
    git checkout $branch
    sed -i 's/.*superdesk-core.git.*/-e ..\/server-core/' server/requirements.txt
    sed -i -re 's/("superdesk-core":).*/\1 "file:..\/client-core"/' client/package.json

    git clone $github/superdesk-core.git server-core
    git clone $github/superdesk-client-core.git client-core
fi
unset repo github branch
