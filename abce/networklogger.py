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
from __future__ import division


class NetworkLogger:
    """ NetworkLogger logs a network. It has to be initialized in start.py.
        In the agents log_network has to be called. Optionally log_agent, can
        be called in order to save agent attributes.

        .. automethod:: abce.Simulation.network
    """
    def log_agent(self, color='blue', style='filled', shape='circle'):
        """ log_agent is optional. It can log agent attributes.

        Args:
            color:
                matplotlib color, default='blue'
            style:
                networkx style, default='filled'
            shape:
                networkx shape, default='circle'
        """
        try:
            if self.round % self._network_drawing_frequency == 0:
                self.logger_connection.put(('node', self.round, ((self.group, self.idn), color, style, shape)))
        except TypeError:
            raise SystemExit("ABCE Error: simulation.network(.) needs to be called in start.py")


    def log_network(self, list_of_nodes):
        """ loggs a network. List of nodes is a list with the numbers of all agents,
        this agent is connected to.

        Args:
            list_of_nodes:
                list of nodes that the agent is linked to. A list of noteds must have
                the following format: [('agent_group', agent_idn), ('agent_group', agent_idn), ...]
                If your
            color:
                integer for the color
            style(True/False):
                filled or not
            shape(True/False):
                form of the bubble
        """
        try:
            if self.round % self._network_drawing_frequency == 0:
                self.logger_connection.put(('edges', self.round, ((self.group, self.idn), list_of_nodes)))
        except TypeError:
            raise SystemExit("ABCE Error: simulation.network(.) needs to be called in start.py")
