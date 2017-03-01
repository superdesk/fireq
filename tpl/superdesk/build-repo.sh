## prepare source code
repo={{repo_core}}{{^repo_core}}{{repo}}{{/repo_core}}
[ -d $repo ] || mkdir $repo
cd $repo
if [ ! -d $repo/.git ]; then
    git init
    git remote add origin {{repo_remote}}
fi

cd $repo
repo_ref={{repo_ref}}
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
