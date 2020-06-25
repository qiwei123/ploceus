# -*- coding: utf-8 -*-
from ploceus.helper import run, sudo

from . import files


MANAGER = 'DEBIAN_FRONTEND=noninteractive apt-get'


def update_index(quiet=True):

    options = ''
    if quiet:
        options = ' --quiet'

    sudo('%s %s update' % (MANAGER, options), quiet=quiet)


def is_installed(pkg):
    if run('dpkg -s %s' % pkg,
           quiet=True, _raise=False, silence=True).failed:
        return False
    return True


def install(packages, update=False, options=None, version=None):
    if update:
        update_index()
    if options is None:
        options = []
    if isinstance(packages, str):
        packages = [packages]
    if version:
        packages = ['{}={}'.format(x, version) for x in packages]
    packages = ' '.join(packages)
    options.append('--quiet')
    options.append('--assume-yes')
    options = ' '.join(options)
    cmd = '%s install %s %s' % (MANAGER, options, packages)
    sudo(cmd)


def uninstall(packages, purge=False, options=None):
    action = 'remove'
    if purge:
        action = 'purge'
    if options is None:
        options = []
    if not isinstance(packages, str):
        packages = ' '.join(packages)
    options.append('--assume-yes')
    options = ' '.join(options)
    cmd = '%s %s %s %s' % (MANAGER, action, options, packages)
    sudo(cmd)


def last_update_time():
    STAMP = '/var/lib/apt/periodic/ploceus-update-success-stamp'
    if not files.is_file(STAMP):
        return -1
    return files.getmtime(STAMP)


def apt_key_exists(key_id):
    _ = run('apt-key list | grep %s' % key_id, _raise=False, quiet=True)
    if _.stdout:
        return True
    return False


def add_apt_key(url):
    run('curl -s %s | sudo apt-key add -' % url)
