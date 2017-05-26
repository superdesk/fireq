{{>superdesk/build.sh}}

# 3.0.9, 3.1.0 versions need bower
cd {{repo_client}}
if [ -f bower.json ]; then
    npm i bower
    time bower --allow-root install
fi
