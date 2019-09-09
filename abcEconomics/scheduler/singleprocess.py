""" Copyright 2012 Davoud Taghawi-Nejad

 Module Author: Davoud Taghawi-Nejad

 abcEconomics is open-source software. If you are using abcEconomics for your research you are
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
from collections import ChainMap
import re


class SingleProcess(object):
    """ This is a container for all agents. It exists only to allow for multiprocessing with MultiProcess.
    """

    def __init__(self):
        self.agents = {}

    def add_agents(self, Agent, simulation_parameters, agent_parameters, default_sim_params, maxid):
        """appends an agent to a group """
        if isinstance(agent_parameters, int):
            agent_parameters = ([] for _ in range(agent_parameters))

        names = {}
        for id, ap in enumerate(agent_parameters, maxid):
            agent = Agent(id, ap, {**default_sim_params, **simulation_parameters})
            agent.init(**ChainMap(simulation_parameters, ap))
            agent._str_name = re.sub('[^0-9a-zA-Z_]', '', str(agent.name))
            names[agent.name] = agent.name
            assert agent.name not in self.agents, ('Two agents with the same name %s' % str(agent.name))
            self.agents[agent.name] = agent
        return names

    def delete_agents(self, names):
        for name in names:
            self.agents.pop(name, None)

    def do(self, names, command, args, kwargs):
        self.rets = []
        for name in names:
            ret = self.agents[name]._execute(command, args, kwargs)
            self.rets.append(ret)

    def post_messages(self, names):
        for name in names:
            self.agents[name]._post_messages(self.agents)
        return self.rets

    def advance_round(self, time, str_time):
        for agent in self.agents.values():
            agent._advance_round(time, str_time)

    def group_names(self):
        return self.agents.keys()
