# -*- coding: utf-8 -*-
import os
import logging
import sys

import ploceus.colors as color
from ploceus.common import get_current_context

LOGGER = logging.getLogger("ploceus.general")

# decpreated name
logger = LOGGER


def log(msg, prefix=''):
    """
    mainly for helper output
    """
    context = get_current_context()
    hostname = color.green(context.hostname)
    if prefix:
        prefix = prefix + ': '
    output = '[{}] {}{}'.format(hostname, prefix, msg)
    # always use INFO level
    logging.getLogger("ploceus.helper").info(output)


def setupLogger(**options):
    debug = options.get('debug', False) or os.environ.get('PLOCEUS_DEBUG')

    # helper logger is static
    logger = logging.getLogger('ploceus.helper')
    logger.handlers.clear()
    hdl = logging.StreamHandler(sys.stdout)
    logFmt = '%(message)s'
    if debug:
        logFmt = '%(asctime)s| %(message)s'
    hdl.setFormatter(logging.Formatter(logFmt))
    hdl.setLevel(logging.INFO)
    logger.addHandler(hdl)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    # cli logger is static, only used from cli entrypoint
    logger = logging.getLogger('ploceus.cli')
    logger.handlers.clear()
    hdl = logging.StreamHandler(sys.stdout)
    hdl.setFormatter(logging.Formatter('%(asctime)s|%(levelname)s| %(message)s'))
    hdl.setLevel(logging.INFO)
    logger.addHandler(hdl)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    logFmt = '%(asctime)s|%(levelname)s| %(message)s'
    lvl = logging.INFO
    if debug:
        lvl = logging.DEBUG
        logFmt = ('[%(asctime)s %(levelname)-7s |%(name)s| %(module)s:'
                  '%(lineno)d] %(message)s')

    logger = logging.getLogger('ploceus')
    logger.handlers.clear()
    hdl = logging.StreamHandler(sys.stdout)
    fmt = logging.Formatter(logFmt)
    hdl.setFormatter(fmt)
    hdl.setLevel(lvl)
    logger.addHandler(hdl)
    logger.setLevel(lvl)
    logger.propagate = False
