# -*- coding: utf-8 -*-
from ploceus import tools

from . import files


def user(name, uid, gid,
         shell=None, home=None,
         groups=None, system=None,
         mode='0700'):

    if tools.users.exists(name):
        tools.users.modify_user(name, uid=uid, gid=gid,
                                shell=shell, home=home,
                                groups=groups)
    else:
        tools.users.create_user(name, uid=uid, gid=gid,
                                shell=shell, home=home,
                                groups=groups, system=system)

    # ensure home directory exists, permission and mode.
    files.directory(home, user=name, grp=gid, mode=mode, use_sudo=True)
