# A client on lockfile v3 needs the Node major pinned in its package.json. Base
# containers with nvm provide it. The Ubuntu 18.04 one has no nvm, and official
# Node >= 18 binaries need glibc 2.28, so it gets the unofficial glibc 2.17 build.
if [ "$(jq -r '.lockfileVersion' package-lock.json)" = 3 ]; then
    node_version=v$(jq -r '.volta.node' package.json)
    set +x
    [ -s ~/.nvm/nvm.sh ] && . ~/.nvm/nvm.sh
    if command -v nvm > /dev/null && nvm use ${node_version%%.*}; then
        set -x
    else
        set -x
        node_dir=/opt/node-$node_version
        if [ ! -x $node_dir/bin/node ]; then
            mkdir -p $node_dir
            curl -fsSL https://unofficial-builds.nodejs.org/download/release/$node_version/node-$node_version-linux-x64-glibc-217.tar.gz \
                | tar -xz --strip-components=1 -C $node_dir
        fi
        export PATH=$node_dir/bin:$PATH
        unset node_dir
    fi
    unset node_version
    node --version
fi
