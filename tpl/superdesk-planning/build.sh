{{>superdesk/build.sh}}

cd {{repo_server}}
pip install -Ue ../superdesk-planning

cd {{repo_client}}
npm link ../superdesk-planning
