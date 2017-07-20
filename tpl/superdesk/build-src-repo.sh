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
    unset repo_ref

    {{#priv_repo_remote}}
    # for now use just master by default
    GIT_SSH_COMMAND="ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no" \
    git -C /tmp/ clone {{priv_repo_remote}} sd_custom
    cp -R /tmp/sd_custom/* $repo/
    {{/priv_repo_remote}}
    unset repo
fi
