# -*- coding: utf-8 -*-


def red(value):
    return '\x1b[1;31m%s\x1b[0m' % value


def green(value):
    return '\x1b[1;32m%s\x1b[0m' % value


def yellow(value):
    return '\x1b[1;33m%s\x1b[0m' % value


def blue(value):
    return '\x1b[1;34m%s\x1b[0m' % value


def magenta(value):
    return '\x1b[1;35m%s\x1b[0m' % value


def cyan(value):
    return '\x1b[1;36m%s\x1b[0m' % value
