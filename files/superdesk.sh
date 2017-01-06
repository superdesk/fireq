#!/bin/sh
set -e
repo=/opt/superdesk-deploy

apt-get update
apt-get -y install git

rm -rf $repo
git clone --depth 1 https://github.com/naspeh-sf/deploy.git $repo

cd $repo; ./fire i -e superdesk/master --services --prepopulate

echo "*********************************************************************************"
echo "Installation complete!"
echo "- Open in a bowser the address: http://your_server_address/"
echo "- To login use default credentials:"
echo "    Login: admin"
echo "    Password: admin"
echo "*********************************************************************************"
