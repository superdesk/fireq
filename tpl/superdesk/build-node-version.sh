# Make sure nvm is active
set +x
if [ -s ~/.nvm/nvm.sh ]; then
    source ~/.nvm/nvm.sh
fi
set -x

# Install the correct Node version based on package-lock.json
if grep "lockfileVersion" package-lock.json | grep 3; then
    set +x
    echo "Switching to Node 22"
    nvm use 22
    set -x
fi

