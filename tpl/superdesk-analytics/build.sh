{{>superdesk/build.sh}}

cd {{repo_server}}
pip install -Ue ../analytics

cd {{repo_client}}
npm install ../analytics
