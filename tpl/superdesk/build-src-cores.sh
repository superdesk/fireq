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

    # make sure there are dependencies in client/node_modules
    cd client && time npm install --unsafe-perm
    cd $repo

    sed -i 's/.*superdesk-core.git.*/-e ..\/server-core/' server/requirements.txt
    sed -i -re 's/("superdesk-core":)[^,]*(,?)/\1 "file:..\/client-core"\2/' client/package.json

    git clone $github/superdesk-core.git server-core
    git clone $github/superdesk-client-core.git client-core
fi
unset repo github branch
