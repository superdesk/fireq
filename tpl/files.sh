path=files
if [ -d $path ]; then
    cd $path
    git pull origin files
else
    mkdir $path
    cd $path
    git clone -b files --single-branch https://github.com/superdesk/fireq.git .
fi
