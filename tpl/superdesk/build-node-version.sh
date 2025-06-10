# Make sure nvm is active
source ~/.nvm/nvm.sh

# Install the correct Node version based on package-lock.json
if grep "lockfileVersion" package-lock.json | grep 3; then
    set +x
    echo "Switching to Node 22"
    nvm use 22
    set -x
fi