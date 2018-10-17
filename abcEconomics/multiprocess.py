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


import re
import multiprocessing as mp
from multiprocessing.managers import BaseManager
import traceback
from collections import defaultdict, ChainMap

from .singleprocess import SingleProcess


class MyManager(BaseManager):
    pass


class ProcessorGroup(SingleProcess):
    def __init__(self, batch, queues, processes):
        self.agents = {}
        self.batch = batch
        self.queues = queues
        self.queue = queues[self.batch]
        self.processes = processes

    def add_agents(self, Agent, simulation_parameters, agent_parameters, default_sim_params, maxid):
        """appends an agent to a group """
        if isinstance(agent_parameters, int):
            agent_parameters = ({} for _ in range(agent_parameters))

        names = {}
        _sim_parameters = {**default_sim_params, **simulation_parameters}
        group = _sim_parameters['group']
        for id, ap in enumerate(agent_parameters, maxid):
            agent_name = ap.get('name', (group, id))
            if hash(agent_name) % self.processes == self.batch:
                agent = Agent(id, ap, _sim_parameters, name=agent_name)
                agent.send = agent._send_multiprocessing
                agent._out = defaultdict(list)
                agent.init(**ChainMap(simulation_parameters, ap))
                assert agent.name not in self.agents, ('Two agents with the same name %s' % str(agent.name))
                agent._str_name = re.sub('[^0-9a-zA-Z_]', '', str(agent.name))
                names[agent.name] = agent.name
                agent._processes = self.processes
                self.agents[agent.name] = agent
        return names

    def do(self, names, command, args, kwargs):
        try:
            self.rets = []
            self.post = [[] for _ in range(self.processes)]
            for name in names:
                if hash(name) % self.processes == self.batch:
                    agent = self.agents[name]
                    ret = agent._execute(command, args, kwargs)
                    self.rets.append(ret)
                    pst = agent._post_messages_multiprocessing(self.processes)
                    for o in range(self.processes):
                        self.post[o].extend(pst[o])
        except Exception:
            traceback.print_exc()
            raise

    def post_messages(self, names):
        for i in range(self.processes):
            self.queues[i].put(self.post[i])

        for i in range(self.processes):
            for receiver, envelope in self.queue.get():
                try:
                    self.agents[receiver].inbox.append(envelope)
                except KeyError:
                    print(envelope)
                    raise KeyError("Receiver %s does not exist" % str(name))
        return self.rets


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

    def add_agents(self, Agent, simulation_parameters, agent_parameters, agent_arguments, maxid):
        """appends an agent to a group """
        names = self.pool.map(add_agents_wrapper, jkk(self.processor_groups,
                                                      Agent,
                                                      simulation_parameters,
                                                      agent_parameters,
                                                      agent_arguments,
                                                      maxid))

        return flatten(names)

    def delete_agents(self, names):
        self.pool.map(delete_agents_wrapper, jkk(self.processor_groups, names))

    def do(self, names, command, args, kwargs):
        self.pool.map(wrapper, jkk(self.processor_groups, names, command, args, kwargs))

    def post_messages(self, names):
        return flatten(self.pool.map(post_messages, jkk(self.processor_groups, names)))

    def advance_round(self, time, str_time):
        self.pool.map(advance_round_wrapper, jkk(self.processor_groups, time, str_time))

    def group_names(self):
        return self.processor_groups[0].group_names()


def wrapper(args):
    pg, names, command, args, kwargs = args
    pg.do(names, command, args, kwargs)


def post_messages(args):
    pg, names = args
    return pg.post_messages(names)


def add_agents_wrapper(arg):
    pg, Agent, simulation_parameters, agent_parameters, agent_arguments, maxid = arg
    return pg.add_agents(Agent, simulation_parameters, agent_parameters, agent_arguments, maxid)


def delete_agents_wrapper(arg):
    pg, names = arg
    pg.delete_agents(names)


def advance_round_wrapper(arg):
    pg, time, str_time = arg
    pg.advance_round(time, str_time)


def jkk(iterator, *args):
    for i in iterator:
        yield (i,) + args


def flatten(l):
    return [item for sublist in l for item in sublist]
