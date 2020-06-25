# -*- coding: utf-8 -*-
import logging
import os

from ploceus.inventory import Inventory
import ploceus.logger as logger


class GlobalStore(object):
    """ploceus global store
    """

    tasks = {}
    inventory = Inventory()

    def add_task(self, task):
        self.tasks[task.name] = task


# 2018-08-14
# deprecated 不使用全局变量
g = GlobalStore()


def setup(**options):
    g.inventory.setup()
    logger.setupLogger(**options)
