# -*- coding: utf-8 -*-
from ploceus import tools

from ploceus.colors import cyan
from ploceus.logger import log


def package(pkg, update=None, version=None):
    log('install %s' % pkg, prefix=cyan('deb'))
    if tools.deb.is_installed(pkg):
        return

    tools.deb.install(pkg, update=update, version=version)


def packages(pkgs, update=False):
    package(" ".join(pkgs), update=update)


def uptodate_index(quiet=True, max_age=3600):
    tools.files.upload_file('/etc/apt/apt.conf.d/15-ploceus-update-stamp',
                            contents="""
APT::Update::Post-Invoke-Success {"touch /var/lib/apt/periodic/ploceus-update-success-stamp 2>/dev/null || true";};
                      """)

    if tools.system.time() - tools.deb.last_update_time() > max_age:
        log('updateing apt index', prefix=cyan('deb'))
        tools.deb.update_index(quiet=quiet)
    log('apt index updated', prefix=cyan('deb'))


def key(key_id, url):
    if not tools.deb.apt_key_exists(key_id):
        tools.deb.add_apt_key(url)
    log('added apt key "%s"' % key_id, prefix=cyan('deb'))


def source(name, uri, distribution, *components, **kwargs):
    arch = ''
    if 'arch' in kwargs:
        arch = '[arch=%s]' % kwargs.get('arch')

    path = '/etc/apt/sources.list.d/%s.list' % name
    components = ' '.join(components)

    contents = 'deb %s %s %s %s\n' % (arch, uri, distribution, components)
    tools.files.upload_file(path, contents=contents, use_sudo=True)
    log('added apt repo "%s"' % name, prefix=cyan('deb'))
