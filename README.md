```
$ ./sd -h
usage: sd [-h] {install,i,lxc-base} ...

positional arguments:
  {install,i,lxc-base}  commands

optional arguments:
  -h, --help            show this help message and exit

$ ./sd lxc-base
$ ./sd i -s root@10.0.3.187 --dev
$ ssh root@10.0.3.187 "source /opt/repos/.env/bin/activate; C_FORCE_ROOT=1 honcho -d /opt/repos/ start"
```
