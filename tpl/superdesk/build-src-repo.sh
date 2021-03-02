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

# Merge the `.fireq.json` file from the source repo (i.e. the repo/branch of a PR, or a customers repo/branch)
_merge_json_from_cwd
