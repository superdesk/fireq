repo={{repo}}
github=https://github.com/superdesk
branch=${branch:-master}

# Overrides the `branch` if it is set in the `.fireq.json` file
if [ -f {{fireq_json}} ] && [ `jq ".superdesk_branch?" {{fireq_json}}` != "null" ]; then
    branch=`jq ".superdesk_branch?" {{fireq_json}}`
fi

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
