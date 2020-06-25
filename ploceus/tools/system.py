# -*- coding: utf-8 -*-
from ploceus.helper import run


def time():
    return int(run('date +%s', quiet=True, silence=True).stdout.strip())


def cpus():
    return int(run(('cat /proc/cpuinfo | '
                    'grep -P "processor\t:"'
                    ' | wc -l'), quiet=True, silence=True).stdout.strip())


def distro():
    """
    发行版的名称
    """
    return run('lsb_release -s -i', quiet=True, silence=True).stdout.strip()


def codename():
    """
    发行版版本的代号
    """
    return run('lsb_release -s -c', quiet=True, silence=True).stdout.strip()


def release():
    """
    发行版版本的发行版本
    """
    return run('lsb_release -s -r', quiet=True, silence=True).stdout.strip()
