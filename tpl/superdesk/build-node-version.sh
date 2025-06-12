# Make sure nvm is active
source ~/.nvm/nvm.sh

# Install the correct Node version based on package-lock.json
<<<<<<< HEAD
grep "lockfileVersion" package-lock.json | grep 3 && nvm use 22
=======
if grep "lockfileVersion" package-lock.json | grep 3; then
    set +x
    echo "Switching to Node 22"
    nvm use 22
    set -x
fi
>>>>>>> f19562c234f5ce2397d25e97ef792ea3298069f2
