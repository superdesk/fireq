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

    # git clone $github/superdesk-core.git server-core
    # git clone $github/superdesk-client-core.git client-core
fi
unset repo github branch
