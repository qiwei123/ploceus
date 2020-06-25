# -*- coding: utf-8 -*-
import hashlib
import uuid

from ploceus import tools
from ploceus.colors import cyan
from ploceus.context import cd
from ploceus.helper import run, sudo
from ploceus.logger import log


from .files import directory


def get_url(url, path, user=None, grp=None, mode=None,
            sha1sum=None, use_sudo=False):

    log('%s -> %s' % (url, path), prefix=cyan('get_url'))

    if sha1sum and tools.files.is_file(path):
        if sha1sum.lower() == tools.files.sha1sum(path):
            return

    tools.network.download(url, path, use_sudo=use_sudo)

    if (user and user != tools.files.owner(path)) or \
       (grp and grp != tools.files.group(path)):
        tools.files.chown(path, user=user, grp=grp, use_sudo=use_sudo)

    if mode and mode != tools.files.mode(path):
        tools.files.chmod(path, mode, use_sudo=use_sudo)

    if sha1sum:
        newsum = tools.files.sha1sum(path)
        if sha1sum.lower() != newsum:
            msg = (
                'sha1sum not match for {} -> {}\n'
                'real:   "{}"\n'
                'expect: "{}"'
            ).format(url, path, newsum, sha1sum)
            raise RuntimeError(msg)


def get_tarball(url, dest, probe=None, user=None, grp=None,
                mode=None, sha1sum=None, use_sudo=None):
    """
    download tarball and extract to dest path.

    ``probe'' is use to detect target existence
    note that ``sha1sum'' is only used to verify download
    """
    log('%s -> %s' % (url, dest), prefix=cyan('get_tarball'))

    binary = 'tar xf'
    suffix = ''

    # check extension
    if url.endswith('.zip'):
        binary = 'unzip'
        suffix = 'zip'
    elif url.endswith('.tar.gz'):
        binary = 'tar xf'
        suffix = 'tgz'
    elif url.endswith('.tar.bz2'):
        binary = 'tar xf'
        suffix = 'tbz2'
    elif url.endswith('.tar.xz'):
        binary = 'tar xf'
        suffix = 'xz'
    elif url.endswith('.tgz'):
        binary = 'tar xf'
        suffix = 'tgz'
    elif url.endswith('.tbz2'):
        binary = 'tar xf'
        suffix = 'tbz2'
    elif url.endswith('.txz'):
        binary = 'tar xf'
        suffix = 'txz'
    elif url.endswith('.tar'):
        binary = 'tar xf'
        suffix = 'tar'
    elif url.endswith('.gz'):
        binary = 'gzip -d'
        suffix = 'gz'
    elif url.endswith('.bz2'):
        binary = 'bzip2 -d'
        suffix = 'bz2'
    elif url.endswith('.bz'):
        binary = 'bzip2 -d'
        suffix = 'bz'
    else:
        raise RuntimeError('unsupported extension')

    if probe:
        if tools.files.exists(probe):
            return

    b = str(uuid.uuid4()).encode()
    m = hashlib.sha1()
    m.update(b)
    tmp = m.hexdigest()[:7]
    tmp = '/tmp/{}.{}'.format(tmp, suffix)

    tools.network.download(url, tmp, use_sudo=use_sudo)

    if sha1sum:
        newsum = tools.files.sha1sum(tmp)
        if sha1sum.lower() != newsum:
            raise RuntimeError(
                'sha1sum {} not matched for {} -> {}'.format(
                    newsum, url, tmp,
                ))

    if not tools.files.is_dir(dest):
        directory(
            dest, user=user, grp=grp, use_sudo=use_sudo)

    _ = (use_sudo and sudo) or run
    with cd(dest):
        cmd = '{} {}'.format(binary, tmp)
        _(cmd)

    # FIXME: directory must be executable
    if user and grp:
        tools.files.chown(
            dest, user=user, grp=grp,
            use_sudo=use_sudo, recursive=True)

    if tools.files.exists(tmp):
        _('rm {}'.format(tmp))
