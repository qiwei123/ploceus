# -*- coding: utf-8 -*-
from ploceus.api import run, run_task


def task1():
    run('date')


def test_run():
    run_task(task1, ['localhost'])
