# -*- coding: utf-8 -*-
from ploceus.helper import sudo
from ploceus.exceptions import ArgumentError

def create_group(name, gid):
    return sudo('groupadd -g %s %s' % (gid, name))


def change_group(name, new_name=None, gid=None):
    command = 'groupmod '
    if not(new_name or gid):
        raise ArgumentError('must specify new_name or gid')

    if new_name:
        command += ' -n %s' % new_name

    if gid:
        command += ' -g %s' % gid

    command += ' %s' % name
    return sudo(command)
