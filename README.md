# Install a Superdesk

## Fresh Ubuntu 16.04
```sh
curl https://raw.githubusercontent.com/naspeh-sf/deploy/master/files/superdesk-10.sh | sudo sh
```

## LXC container
```sh
apt-get install lxc

./fire lxc-init -n sd0
./fire i --lxc-name=sd0 --services --prepopulate

# more options
./fire -h
```

# Install a Liveblog

## Fresh Ubuntu 16.04
```sh
curl https://raw.githubusercontent.com/naspeh-sf/deploy/master/files/liveblog.sh | sudo sh
```
# Run github integration server
```sh
gunicorn web:app --bind localhost:8080 --worker-class aiohttp.worker.GunicornWebWorker --reload
```
