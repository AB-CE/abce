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


import multiprocessing as mp
from multiprocessing.managers import BaseManager
import traceback
from collections import defaultdict


class MyManager(BaseManager):
    pass


class ProcessorGroup:
    def __init__(self, batch, queues):
        self.agents = {}
        self.batch = batch
        self.queues = queues
        self.queue = queues[self.batch]

    def new_group(self, group):
        """ Creates a new group. """
        self.agents[group] = []

    def insert_or_append(self, group, ids, Agent, simulation_parameters, agent_parameters, agent_arguments):
        """appends an agent to a group """
        for id, ap in zip(ids, agent_parameters):
            if id % 4 == self.batch:
                agent = Agent(id, simulation_parameters, ap, **agent_arguments)
                agent._send = agent._send_multiprocessing
                agent._out = defaultdict(list)
                agent.init(simulation_parameters, ap)
                if len(self.agents[group]) <= id // 4:
                    self.agents[group].append(agent)
                else:
                    self.agents[group][id // 4] = agent

    def advance_round(self, time):
        for agents in self.agents.values():
            for agent in agents:
                if agent is not None:
                    agent._advance_round(time)

    def delete_agent(self, group, id):
        assert self.agents[group][id // 4].id == id
        assert self.agents[group][id // 4].group == group
        self.agents[group][id // 4] = None

    def do(self, groups, ids, command, args, kwargs):
        try:
            rets = []
            post = [[], [], [], []]
            for group, iss in zip(groups, ids):
                for i in iss:
                    if i is not None:
                        if i % 4 == self.batch:
                            agent = self.agents[group][i // 4]
                            ret = agent._execute(command, args, kwargs)
                            rets.append(ret)
                            pst = agent._post_messages_multiprocessing(4)
                            for o in range(4):
                                post[o].extend(pst[o])

            for i in range(4):
                self.queues[i].put(post[i])

            for i in range(4):
                for receiver_group, receiver_id, envelope in self.queue.get():
                    self.agents[receiver_group][receiver_id // 4].inbox.append(envelope)
            return rets
        except Exception as e:
            traceback.print_exc()
            raise

    def keys(self):
        return self.agents.keys()


class MultiProcess(object):
    """ This is a container for all agents. It exists only to allow for multiprocessing with MultiProcess.
    """
    def __init__(self):
        manager = mp.Manager()
        self.queues = [manager.Queue() for _ in range(4)]
        self.pool = mp.Pool(4)
        MyManager.register('ProcessorGroup', ProcessorGroup)
        self.processor_groups = []
        self.managers = []
        for i in range(4):
            manager = MyManager()
            manager.start()
            self.managers.append(manager)
            pg = manager.ProcessorGroup(i, self.queues)
            self.processor_groups.append(pg)

    def new_group(self, group):
        """ Creates a new group. """
        for pg in self.processor_groups:
            pg.new_group(group)

    def insert_or_append(self, group, ids, Agent, simulation_parameters, agent_parameters, agent_arguments):
        """appends an agent to a group """
        lpg = len(self.processor_groups)
        self.pool.map(insert_or_append_wrapper, zip(self.processor_groups, [group] * lpg, [ids] * lpg, [Agent] * lpg, [simulation_parameters] * lpg, [agent_parameters] * lpg, [agent_arguments] * lpg))

    def delete_agent(self, group, id):
            self.processor_groups[id % 4].delete_agent(group, id)

    def do(self, groups, ids, command, args, kwargs):
        lpg = len(self.processor_groups)
        ret = self.pool.map(wrapper, zip(self.processor_groups, [groups] * lpg, [ids] * lpg, [command] * lpg, [args] * lpg, [kwargs] * lpg))
        sorted_ret = []
        for i in range(len(ret[0])):
            for pg in ret:
                try:
                    sorted_ret.append(pg[i])
                except IndexError:
                    pass
        return sorted_ret

    def advance_round(self, time):
        for pg in self.processor_groups:
            pg.advance_round(time)

    def group_names(self):
        return self.processor_groups[0].keys()


def wrapper(arg):
    pg, groups, ids, command, args, kwargs = arg
    return pg.do(groups, ids, command, args, kwargs)


def insert_or_append_wrapper(arg):
    pg, group, ids, Agent, simulation_parameters, agent_parameters, agent_arguments = arg
    return pg.insert_or_append(group, ids, Agent, simulation_parameters, agent_parameters, agent_arguments)
