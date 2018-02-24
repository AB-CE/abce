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
from collections import defaultdict, ChainMap


class MyManager(BaseManager):
    pass


class ProcessorGroup:
    def __init__(self, batch, queues, processes):
        self.agents = {}
        self.batch = batch
        self.queues = queues
        self.queue = queues[self.batch]
        self.processes = processes

    def new_group(self, group):
        """ Creates a new group. """
        self.agents[group] = []

    def insert_or_append(self, group, ids, free_ids, Agent, simulation_parameters, agent_parameters, agent_arguments):
        """appends an agent to a group """
        if isinstance(agent_parameters, int):
            agent_parameters = ([] for _ in range(agent_parameters))

        for ap in agent_parameters:
            if free_ids:
                id = free_ids.popleft()
                ids[id] = id
            else:
                id = len(ids)
                ids.append(id)
            if id % self.processes == self.batch:
                agent = Agent(id, simulation_parameters, ap, **agent_arguments)
                agent._send = agent._send_multiprocessing
                agent._out = defaultdict(list)
                agent.init(**ChainMap(simulation_parameters, ap))
                agent._processes = self.processes
                if len(self.agents[group]) <= id // self.processes:
                    self.agents[group].append(agent)
                else:
                    self.agents[group][id // self.processes] = agent
        return ids

    def advance_round(self, time):
        for agents in self.agents.values():
            for agent in agents:
                if agent is not None:
                    agent._advance_round(time)

    def delete_agents(self, group, ids):
        for id in ids:
            if id % self.processes == self.batch:
                assert self.agents[group][id // self.processes].id == id
                assert self.agents[group][id // self.processes].group == group
                self.agents[group][id // self.processes] = None

    def do(self, groups, ids, command, args, kwargs):
        try:
            self.rets = []
            self.post = [[] for _ in range(self.processes)]
            for group, iss in zip(groups, ids):
                for i in iss:
                    if i is not None:
                        if i % self.processes == self.batch:
                            agent = self.agents[group][i // self.processes]
                            ret = agent._execute(command, args, kwargs)
                            self.rets.append(ret)
                            pst = agent._post_messages_multiprocessing(self.processes)
                            for o in range(self.processes):
                                self.post[o].extend(pst[o])
        except Exception:
            traceback.print_exc()
            raise

    def post_messages(self, groups, ids):
        for i in range(self.processes):
            self.queues[i].put(self.post[i])

        for i in range(self.processes):
            for receiver_group, receiver_id, envelope in self.queue.get():
                self.agents[receiver_group][receiver_id // self.processes].inbox.append(envelope)
        return self.rets

    def keys(self):
        return self.agents.keys()


class MultiProcess(object):
    """ This is a container for all agents. It exists only to allow for multiprocessing with MultiProcess.
    """
    def __init__(self, processes):
        manager = mp.Manager()
        self.queues = [manager.Queue() for _ in range(processes)]
        self.pool = mp.Pool(processes)
        MyManager.register('ProcessorGroup', ProcessorGroup)
        self.processor_groups = []
        self.managers = []
        for i in range(processes):
            manager = MyManager()
            manager.start()
            self.managers.append(manager)
            pg = manager.ProcessorGroup(i, self.queues, processes)
            self.processor_groups.append(pg)

    def new_group(self, group):
        """ Creates a new group. """
        for pg in self.processor_groups:
            pg.new_group(group)

    def insert_or_append(self, group, ids, free_ids, Agent, simulation_parameters, agent_parameters, agent_arguments):
        """appends an agent to a group """
        ids = self.pool.map(insert_or_append_wrapper, jkk(self.processor_groups,
                                                          group,
                                                          ids,
                                                          free_ids,
                                                          Agent,
                                                          simulation_parameters,
                                                          agent_parameters,
                                                          agent_arguments))
        return ids[0]

    def delete_agents(self, group, ids):
        self.pool.map(delete_agents_wrapper, jkk(self.processor_groups, group, ids))

    def do(self, groups, ids, command, args, kwargs):
        self.pool.map(wrapper, jkk(self.processor_groups, groups, ids, command, args, kwargs))

    def post_messages(self, groups, ids):
        ret = self.pool.map(post_messages, jkk(self.processor_groups, groups, ids))
        return sort_ret(ret)

    def advance_round(self, time):
        self.pool.map(advance_round_wrapper, jkk(self.processor_groups, time))

    def group_names(self):
        return self.processor_groups[0].keys()


def wrapper(args):
    pg, groups, ids, command, args, kwargs = args
    pg.do(groups, ids, command, args, kwargs)


def post_messages(args):
    pg, groups, ids = args
    return pg.post_messages(groups, ids)


def insert_or_append_wrapper(arg):
    pg, group, ids, free_ids, Agent, simulation_parameters, agent_parameters, agent_arguments = arg
    return pg.insert_or_append(group, ids, free_ids, Agent, simulation_parameters, agent_parameters, agent_arguments)


def delete_agents_wrapper(arg):
    pg, group, ids = arg
    pg.delete_agents(group, ids)


def advance_round_wrapper(arg):
    pg, time = arg
    pg.advance_round(time)


def sort_ret(ret):
    sorted_ret = []
    for i in range(len(ret[0])):
        for pg in ret:
            try:
                sorted_ret.append(pg[i])
            except IndexError:
                pass
    return sorted_ret


def jkk(iterator, *args):
    for i in iterator:
        yield (i,) + args
