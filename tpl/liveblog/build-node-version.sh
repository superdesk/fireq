# The Liveblog base container is Ubuntu 18.04 (glibc 2.27), where official
# Node >= 18 binaries do not run (they need glibc 2.28), so a client on
# lockfile v3 gets the unofficial glibc 2.17 build of its pinned Node.
if [ "$(jq -r '.lockfileVersion' package-lock.json)" = 3 ]; then
    node_version=v$(jq -r '.volta.node' package.json)
    node_dir=/opt/node-$node_version
    if [ ! -x $node_dir/bin/node ]; then
        mkdir -p $node_dir
        curl -fsSL https://unofficial-builds.nodejs.org/download/release/$node_version/node-$node_version-linux-x64-glibc-217.tar.gz \
            | tar -xz --strip-components=1 -C $node_dir
    fi
    export PATH=$node_dir/bin:$PATH
    unset node_version node_dir
    node --version
fi
