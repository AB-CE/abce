""" Copyright 2012 Davoud Taghawi-Nejad

 Module Author: Davoud Taghawi-Nejad

 ABCE is open-source software. If you are using ABCE for your research you are
 requested the quote the use of this software.

 Licensed under the Apache License, Version 2.0 (the "License"); you may not
 use this file except in compliance with the License and quotation of the
 author. You may obtain a copy of the License at
       http://www.apache.org/licenses/LICENSE-2.0
 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
 License for the specific language governing permissions and limitations under
 the License.
"""
# pylint: disable=W0212, C0111


class SingleProcess(object):
    """ This is a container for all agents. It exists only to allow for multiprocessing with MultiProcess.
    """
    def __init__(self):
        self.agents = {}

    def new_group(self, group):
        """ Creates a new group. """
        self.agents[group] = []

    def append(self, agent, group, id):
        """appends an agent to a group """
        self.agents[group].append(agent)

    def get_agents(self, groups, ids):
        """ Iterate over agents in ids in several groups

        Args:
            groups:
                array of group names
            ids:
                array of the same length as group names, which
                contains arrais with the id's of individual agent.

        Example::

            get_agents([agentsA, agentsB ], [[1,3,4], [1,5,6]])
        """
        for group, iss in zip(groups, ids):
            for i in iss:
                if i is not None:
                    yield self.agents[group][i]

    def get(self, group, id):
        return self.agents[group][id]
