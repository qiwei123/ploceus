## Ploceus

Ploceus is inspired by Fabric and Ansible, but with plain Python code.

All I want is just a (rather naive) library to get the things done in Python3.

Ploceus is powered by paramiko.

`Ploceusfile.py` or `Ploceusfile`

```
# -*- coding: utf-8 -*-
from ploceus.api import task
from ploceus.api import run, sudo

@task
def test():
    run('date')
    sudo('id')
```

list tasks.

```
$ /path/to/ploceus -l
```

run tasks with hosts.

```
$ /path/to/ploceus -H example.com test
```

## Known issue

- running apt on same host concurrently will cause `/var/apt/pkg/lock` problem
  may be locking first?


## License

GPL-2
