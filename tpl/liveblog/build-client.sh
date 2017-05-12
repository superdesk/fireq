### Client part
{{>add-node.sh}}

cd {{repo_client}}
npm i grunt-cli
time npm install

if [ -f bower.json ]; then
    # 3.0.9, 3.1.0 versions need bower
    npm i bower
    time bower --allow-root install
fi
