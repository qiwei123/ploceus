# -*- coding: utf-8 -*-
import yaml
import os

from ploceus.exceptions import NoGroupFoundError




class Inventory(object):

    inventory = None
    _groups = {}

    def __init__(self, inventory=None):
        self.inventory = inventory

    def setup(self):
        if self.inventory is None:
            self.find_inventory()

        self._load_inventory()


    def _load_inventory(self):

        if self.inventory is None:
            return

        self._groups = dict()

        inventory = self.inventory

        if os.path.isfile(inventory):
            file_names = [inventory]
        elif os.path.isdir(inventory):
            file_names = filter(
                lambda x: os.path.isfile,
                map(lambda x: os.path.join(inventory, x),
                    os.listdir(inventory)))
        else:
            raise ValueError('not a valid invetory file: %s' % inventory)

        for fname in file_names:
            self._groups.update(self._parse_inventory(fname))


    def _parse_inventory(self, fname):
        with open(fname) as f:
            return yaml.safe_load(f.read())

    @property
    def empty(self):
        return len(self._groups.keys()) <= 0


    def list_inventory(self):
        if len(self._groups.keys()) == 0:
            print('\n    No group defined.\n')

        print('\n  Available groups:\n')
        for name in sorted(self._groups.keys()):
            if 'hosts' in self._groups.get(name):
                print('\t%s' % name)

        print('\n')


    def get_target_hosts(self, group_name):
        group = self._groups.get(group_name)
        if group is None:
            raise NoGroupFoundError('no group named %s found' % group_name)

        return group


    def get_target_host(self, hostname):
        if self.empty:
            return {}

        host_vars = self._groups.get(hostname) or {}
        return host_vars


    def find_inventory(self):
        if os.path.exists('hosts'):
            self.inventory = 'hosts'
