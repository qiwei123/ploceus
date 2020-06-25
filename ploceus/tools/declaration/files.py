# -*- coding: utf-8 -*-
from ploceus import tools


def directory(path, user=None, grp=None,
              mode=None, recursive=False, use_sudo=None):

    if not tools.files.is_dir(path):
        tools.files.mkdir(path, user=user, grp=grp,
                          use_sudo=use_sudo)
        return

    if user and grp:
        tools.files.chown(path, user=user, grp=grp,
                          recursive=recursive, use_sudo=use_sudo)

    if mode:
        tools.files.chmod(path, mode=mode,
                          recursive=recursive, use_sudo=use_sudo)


def file(path, user=None, grp=None,
         mode=None, use_sudo=None):

    if (user and (tools.files.owner(path) != user)) or\
       ((grp and tools.files.group(path) != grp)):
        tools.files.chown(path, user=user, grp=grp,
                          use_sudo=use_sudo)

    if mode and (tools.files.mode(path) != mode):
        tools.files.chmod(path, mode=mode,
                          use_sudo=use_sudo)
