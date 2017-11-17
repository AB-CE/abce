from collections import defaultdict, deque
import traceback
from time import sleep
import random


class ProcessorGroup(object):
    def __init__(self, num_managers, batch):
        self.agents = {}
        self.batch = batch
        self.num_managers = num_managers
        self.mymessages = list()
        self.free_ids = defaultdict(deque)

    def add_group(self, Agent, num_agents_this_group, agent_args, parameters,
                  agent_parameters, agent_params_from_sim):
        group = agent_args['group']
        self.agents[group] = []
        self.apfs = agent_params_from_sim
        for i in range(self.batch, num_agents_this_group, self.num_managers):
            agent = self.make_an_agent(Agent, id=i, agent_args=agent_args,
                                       parameters=parameters,
                                       agent_parameters=agent_parameters[i])
            self.agents[group].append(agent)

    def append(self, Agent, agent_args, parameters, agent_parameters):
        group = agent_args['group']
        try:
            id = self.free_ids[group].popleft()
        except IndexError:
            id = (len(self.agents[group])) * self.num_managers + self.batch
            self.agents[group].append(None)
        agent = self.make_an_agent(
            Agent, id, agent_args, parameters, agent_parameters)
        self.agents[group][id // self.num_managers] = agent
        return id

    def make_an_agent(self, Agent, id, agent_args,
                      parameters, agent_parameters):
        agent_args['num_managers'] = self.num_managers
        agent = Agent(id=id, **agent_args)
        for good, duration in self.apfs['expiring']:
            agent._declare_expiring(good, duration)
        for good in self.apfs['perishable']:
            agent._register_perish(good)
        for resource, units, product in self.apfs['resource_endowment']:
            agent._register_resource(resource, units, product)
        try:
            agent.init(parameters, agent_parameters)
        except AttributeError:
            if 'init' not in dir(agent):
                print("Warning: agent %s has no init function" % agent.group)
            else:
                raise
        except KeyboardInterrupt:
            return None
        except Exception:
            sleep(random.random())
            traceback.print_exc()
            raise Exception()
        return agent

    def execute(self, groups, command, messages, args, kwargs):
        try:
            out = [[] for _ in range(self.num_managers + 1)]
            self.put_messages_in_pigeonbox(messages)
            for group in groups:
                for agent in self.agents[group]:
                    try:
                        outmessages = agent._execute(command, args, kwargs)
                        for pgid, msg in enumerate(outmessages):
                            if msg is not None:
                                if pgid == self.batch:
                                    self.mymessages.extend(msg)
                                elif pgid == self.num_managers:
                                    out[pgid].append(msg)
                                else:
                                    out[pgid].extend(msg)
                    except AttributeError:
                        pass
        except Exception:
            traceback.print_exc()
            raise
        return out

    def delete_agent(self, group, id):
        self.agents[group][id // self.num_managers] = None
        self.free_ids[group].append(id)

    def name(self):
        return (self.group, self.batch)

    def execute_advance_round(self, time):
        for group in self.agents.values():
            for agent in group:
                try:
                    agent._advance_round(time)
                except KeyboardInterrupt:
                    return None
                except AttributeError:
                    pass
                except Exception:
                    sleep(random.random())
                    traceback.print_exc()
                    raise Exception()

    def put_messages_in_pigeonbox(self, new_messages):
        for group, id, message in new_messages:
            self.agents[group][id // self.num_managers].inbox.append(message)
        for group, id, message in self.mymessages:
            self.agents[group][id // self.num_managers].inbox.append(message)
        self.mymessages.clear()

    def len(self):
        return sum([len(group) for group in self.agents.values()])

    def repr(self):
        return str(self.batch)

    def __repr__(self):
        return repr()
