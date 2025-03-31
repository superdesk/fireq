# Install the correct Node version
grep "lockfileVersion" package-lock.json | grep 3 && nvm use 20