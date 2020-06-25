# -*- coding: utf-8 -*-
from ploceus.helper import sudo


def exists(name):
    if sudo('getent passwd %s' % name, _raise=False).failed:
        return False
    return True


def create_user(name, uid, gid,
                shell=None, home=None,
                groups=None, system=None):
    command = 'useradd -u %s -g %s' % (uid, gid)
    if shell:
        command += ' -s %s' % shell

    if home:
        command += ' -d %s' % home

    if groups:
        command += ' -G %s' % ','.join(groups)

    if system:
        command += ' --system'

    command += ' %s' % name
    return sudo(command)

def modify_user(name, uid=None, gid=None, new_name=None,
                shell=None, home=None,
                groups=None, system=None):
    command = 'usermod '

    if uid:
        command += ' -u %s' % uid

    if gid:
        command += ' -g %s' % gid

    if new_name:
        command += ' -l %s' % new_name

    if shell:
        command += ' -s %s' % shell

    if home:
        command += ' -d %s' % home

    if groups:
        command += ' -G %s' % ','.join(groups)

    if system:
        command += ' --system'

    command += ' %s' % name
    return sudo(command)


def delete_password(name):
    return sudo('passwd -d %s' % name)
