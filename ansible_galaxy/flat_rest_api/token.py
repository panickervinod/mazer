########################################################################
#
# (C) 2015, Chris Houseknecht <chouse@ansible.com>
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.
#
########################################################################
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import logging
import os
from stat import S_IRUSR, S_IWUSR

import yaml

log = logging.getLogger(__name__)


class GalaxyToken(object):
    ''' Class to storing and retrieving token in ~/.ansible_galaxy '''

    def __init__(self):
        self.file = os.path.expanduser("~") + '/.ansible_galaxy'
        self.log = logging.getLogger(__name__ + '.' + self.__class__.__name__)

        self.config = yaml.safe_load(self.__open_config_for_read())
        if not self.config:
            self.config = {}

    def __open_config_for_read(self):
        if os.path.isfile(self.file):
            self.log.debug('Opened %s', self.file)
            return open(self.file, 'r')
        # config.yml not found, create and chomd u+rw
        f = open(self.file, 'w')
        f.close()
        os.chmod(self.file, S_IRUSR | S_IWUSR)  # owner has +rw
        self.log.debug('Created %s', self.file)
        return open(self.file, 'r')

    def set(self, token):
        self.config['token'] = token
        self.save()

    def get(self):
        return self.config.get('token', None)

    def save(self):
        with open(self.file, 'w') as f:
            yaml.safe_dump(self.config, f, default_flow_style=False)
