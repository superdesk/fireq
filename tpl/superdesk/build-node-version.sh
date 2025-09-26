# Make sure nvm is active
set +x
source ~/.nvm/nvm.sh
set -x

# Install the correct Node version based on package-lock.json
if grep "lockfileVersion" package-lock.json | grep 3; then
    set +x
    echo "Switching to Node 22"
    nvm use 22
    set -x
fi