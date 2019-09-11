{{>superdesk/build.sh}}

cd {{repo_server}}
pip install -Ue ../planning

cd {{repo_client}}
npm link ../planning
