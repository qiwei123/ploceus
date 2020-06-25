# -*- coding: utf-8 -*-
from ploceus.helper import run, sudo
from ploceus.logger import log


def download(url, dest, use_sudo=False):
    _ = (use_sudo and sudo) or run

    log('download: {} => {}'.format(
        url, dest,
    ))

    if run('command -v curl', _raise=False).ok:
        _('curl -s %s -o %s' % (url, dest), quiet=True)
        return
    if run('command -v wget', _raise=False).ok:
        _('wget -q -O %s %s' % (dest, url), quiet=True)
        return
