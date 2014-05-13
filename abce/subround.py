# Copyright 2012 Davoud Taghawi-Nejad
#
# Module Author: Davoud Taghawi-Nejad
#
# ABCE is open-source software. If you are using ABCE for your research you are
# requested the quote the use of this software.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License and quotation of the
# author. You may obtain a copy of the License at
#       http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.
"""
The :class:`abceagent.Agent` class is the basic class for creating your agent. It automatically handles the
possession of goods of an agent. In order to produce/transforme goods you need to also subclass
the :class:`abceagent.Firm` [1]_ or to create a consumer the :class:`abceagent.Household`.

For detailed documentation on:

Trading:
    see :class:`abceagent.Trade`
Logging and data creation:
    see :class:`abceagent.Database` and :doc:`simulation_results`
Messaging between agents:
    see :class:`abceagent.Messaging`.

.. autoexception:: abcetools.NotEnoughGoods

.. [1] or :class:`abceagent.FirmMultiTechnologies` for simulations with complex technologies.
"""
from __future__ import division
import zmq
import multiprocessing
from collections import OrderedDict, defaultdict
from abce.tools import *


class Subround(multiprocessing.Process):
    """ If you initate an agent of this class it tells you approximately in
    which subround you are
    """
    def __init__(self, _addresses):
        multiprocessing.Process.__init__(self)
        self._addresses = _addresses
        self.round = 0

    def run(self):
        self.context = zmq.Context()
        self.commands = self.context.socket(zmq.SUB)
        self.commands.connect(self._addresses['command_addresse'])
        self.commands.setsockopt(zmq.SUBSCRIBE, "")

        while True:
            try:
                address = self.commands.recv()  # catches the group adress.
            except KeyboardInterrupt:
                print('KeyboardInterrupt: %s, Last command: %s in self.commands.recv() to catch own adress ~1888' % (self.name, command))
                breakc
            command = self.commands.recv()
            if command == '_advance_round':
                self.round += 1
            elif command == "!":
                subcommand = self.commands.recv()
                print(subcommand)
                if subcommand == 'die':
                    break
            print("%s %s" % (address, command))
            if command == '_produce_resource_rent_and_labor':
                print("X creates X units of X", self.commands.recv_multipart())

