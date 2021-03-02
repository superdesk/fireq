repo={{repo}}
github=git@github.com:superdesk

# Use the config `superdesk_branch` if set
# Otherwise use the `branch` value passed in
# and default to `master`
branch=`_get_json_value superdesk_branch ${branch:-master}`

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

# Merge the `.fireq.json` file from the superdesk repo/branch
# i.e. `superdesk/qa-02-00`, `superdesk/sams` or `superdesk/planning-develop`
_merge_json_from_cwd

unset repo github branch
