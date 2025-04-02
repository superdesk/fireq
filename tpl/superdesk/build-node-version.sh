# Make sure nvm is active
source ~/.nvm/nvm.sh

# Install the correct Node version based on package-lock.json
grep "lockfileVersion" package-lock.json | grep 3 && nvm use 20