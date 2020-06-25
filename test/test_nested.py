# -*- coding: utf-8 -*-
from ploceus.api import run, run_task


def task1():
    run('hostname')

    run_task(task2, ['yukari'])

    run('hostname')


def task2():
    run('hostname')


def test_nested():
    run_task(task1, ['localhost'])
