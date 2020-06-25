# -*- coding: utf-8 -*-
import argparse
import logging
import os
import sys
import time

import terminaltables

import ploceus
from ploceus import g
from ploceus import ploceusfile
import ploceus.colors as color
from ploceus.exceptions import ArgumentError
from ploceus.executor import run_task
from ploceus.inventory import Inventory
from ploceus.runtime import env


LOGGER = logging.getLogger('ploceus.cli')


class PloceusCLI(object):

    def __init__(self):
        self.ploceusfile = None
        self.hosts = []
        self.task_name = None
        self.group = None
        self.sleep = 0
        self.disable_pubkey = False
        self.password = None

        self.ap = None
        self.cli_options()

    def cli_options(self):
        ap = self.ap = argparse.ArgumentParser()
        ap.add_argument(
            '-l', '--list-tasks', action='store_true',
            help='list all avaiable tasks')
        ap.add_argument(
            '-I', '--list-inventory', action='store_true',
            help='list all avaiable groups of hosts'
        )
        ap.add_argument(
            '-f', '--ploceus-file', help='speicify Ploceusfile')
        ap.add_argument(
            '-H', '--host', action='append', help='specify target host',
            default=[])
        ap.add_argument(
            '-i', '--inventory', help='specify inventory file/directory')
        ap.add_argument(
            '-g', '--group', help='specify hosts group')
        ap.add_argument(
            '-P', '--parallel', action='store_true',
            help='run task across hosts parallelly'
        )
        ap.add_argument(
            '-c', '--concurrency', default=os.cpu_count(),
            help='max concurrency for parallel execution'
        )
        ap.add_argument(
            '-s', '--sleep', default=0, type=int,
            help='sleep between two hosts'
        )
        ap.add_argument(
            '-k', '--disable-pubkey',
            action='store_true',
            help='do not use pubkey to authenticate'
        )
        ap.add_argument(
            '-p', '--password', help='use password to connect'
        )
        ap.add_argument(
            '-q', '--quiet', help='quiet mode, suppress command output',
            action='store_true'
        )
        ap.add_argument(
            '--debug', help='set logging level to debug',
            action='store_true'
        )
        ap.add_argument(
            '--args', help='arguments passing to task',
            action='append', default=[],
        )
        ap.add_argument(
            'task_name', nargs='?',
            help='task name to carry out')

    def run(self):
        # FIXME: 重新定义运行时的参数
        # 并应用到 **Ploceus** 实例中
        _ = self._prepare()

        if isinstance(_, int):
            return _

        results, timecost = self._run(*_)
        self.processResult(results, timecost)
        return 0

    def _prepare(self):
        options = self.ap.parse_args()
        # print(options)

        ploceus_filename = options.ploceus_file
        if options.ploceus_file is None:
            ploceus_filename = ploceusfile.find_ploceusfile()
        else:
            ploceusfile.ploceusfile_from_pyfile(options.ploceus_file)

        if options.list_tasks:
            self.list_tasks()
            return 1

        # FIXME: 加载 inventory 根据配置走
        g.inventory = Inventory(options.inventory)

        # setup ploceus runtime
        ploceus.setup(debug=options.debug)

        if options.list_inventory:
            if g.inventory.empty:
                raise ArgumentError('cannot find inventory.')
            self.list_inventory()
            return 1

        if options.group and g.inventory.empty:
            raise ArgumentError(
                'Specify inventory when using group, please.')

        hosts = options.host or []
        extra_vars = None
        if options.group:
            group_hosts = g.inventory.get_target_hosts(options.group)
            if group_hosts:
                hosts += group_hosts['hosts']
                extra_vars = group_hosts.get('vars')

        if options.disable_pubkey and options.password is None:
            raise ArgumentError(
                '--disable-pubkey required but no --password provided.')

        if options.task_name is None:
            raise ArgumentError(
                'Specify a task to run, please. '
                'You can use -l to list tasks.')

        task = g.tasks.get(options.task_name)
        if task is None:
            print('\n\tunknown task: %s\n' % options.task_name)
            return 1

        kwargs = {}

        if options.args:
            for i in options.args:
                k, v = i.split(':', 1)
                kwargs[k] = v

        if options.quiet:
            env.keep_quiet = True

        # FIXME: 临时措施
        return (task, hosts, ploceus_filename, options, extra_vars, kwargs)

    # FIXME: 临时措施
    def _run(
            self, task, hosts, ploceus_filename, options,
            extra_vars, kwargs):

        LOGGER.info('Ploceusfile: %s' % ploceus_filename)
        LOGGER.info('task_name: %s' % options.task_name)
        LOGGER.info('host: %s' % hosts)
        LOGGER.info('keep_quiet: %s' % options.quiet)
        LOGGER.info('parallel: %s' % options.parallel)
        LOGGER.info('concurrency: %s' % options.concurrency)

        ts = time.time()

        rv = run_task(
            task, hosts,
            sleep=options.sleep,
            parallel=options.parallel,
            ssh_pwd=options.password,
            extra_vars=extra_vars,
            cli_options=options.__dict__,
            **kwargs
        )
        te = time.time()
        timecost = (te - ts)
        return rv, timecost

    def list_tasks(self):
        if len(g.tasks) == 0:
            print('\n  No tasks defined.\n\n')
            return True

        print('\n  Available tasks:\n')
        for name in sorted(g.tasks.keys()):
            print('\t%s' % name)

        print('\n')

    def list_inventory(self):
        g.inventory.list_inventory()

    def processResult(self, results, realTime):
        # FIXME: buggy result
        title = 'execution result'

        tableData = [['Hostname', 'Result OK', 'timecost(s)']]

        print('')
        print('')
        totalTimecost = 0
        for hostname, result in results.items():
            c = color.green
            s = 'OK'
            if not result.ok:
                c = color.red
                s = 'NG'
            row = [c(x) for x in [hostname, s, '{:.3f}'.format(result.timecost)]]
            totalTimecost += result.timecost
            tableData.append(row)
        table = terminaltables.AsciiTable(tableData, title)

        lines = table.table.split('\n')
        indent = 8
        out = '\n'.join([' ' * indent + x for x in lines])
        print(out)

        print('')
        print(' ' * indent + 'total timecost: {:.3f}s'.format(totalTimecost))
        print(' ' * indent + ' real timecost: {:.3f}s'.format(realTime))
        print(' ' * indent + 'speed up: {:.1f}x'.format(
            totalTimecost / realTime))
        print('')
        print('')


def main():
    cli = PloceusCLI()
    return cli.run()


if __name__ == '__main__':
    sys.exit(main())
