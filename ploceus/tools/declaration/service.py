# -*- coding: utf-8 -*-
from ploceus.colors import cyan
from ploceus.logger import log
from ploceus.tools.service import is_running, start, stop, restart, reload


def started(service):
    if not is_running(service):
        start(service)
    log('%s started' % service, prefix=cyan('service'))


def stopped(service):
    if is_running(service):
        stop(service)
    log('%s stopped' % service, prefix=cyan('service'))


def restarted(service):
    if is_running(service):
        restart(service)
    else:
        start(service)
    log('%s restarted' % service, prefix=cyan('service'))


def reloaded(service):
    reload(service)
    log('%s reloaded' % service, prefix=cyan('service'))
