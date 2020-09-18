## prepare source code
repo=${repo:-'{{repo}}'}
[ -d $repo ] || mkdir $repo
cd $repo
if [ ! -d $repo/.git ]; then
    git init
    git remote add origin {{repo_remote}}
    repo_ref=${repo_ref:-'{{repo_ref}}'}
    {{#is_pr}}
    git fetch origin $repo_ref/merge: || git fetch origin $repo_ref/head:
    # TODO: use latest sha for now
    git checkout FETCH_HEAD
    {{/is_pr}}
    {{^is_pr}}
    repo_sha={{repo_sha}}
    git fetch origin $repo_ref:
    git checkout ${repo_sha:-FETCH_HEAD}
    unset repo_sha
    {{/is_pr}}
    unset repo repo_ref
fi

if [ -f .fireq.json ]; then
    # If the `superdesk_branch` config is set in the repo,
    # then we will use that branch from github.com/superdesk/superdesk
    if [ `js ".superdesk_branch?" .fireq.json` != "null" ]; then
        _set_config "superdesk_branch=`jq -r ".superdesk_branch?" .fireq.json`"
    fi
fi
