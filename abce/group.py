from collections import defaultdict
from pprint import pprint

class Group(object):
    def __init__(self, sim, groups):
        self.sim = sim
        self.num_managers = sim.processes
        self._processor_groups = sim._processor_groups
        self.groups = groups
        self.do = self.execute_parallel if sim.processes > 1 else self.execute_serial

    def __add__(self, g):
        return  Group(self.sim, self.groups + g.groups)

    def __radd__(self, g):
        if isinstance(g, Group):
            return __add__(g)
        else:
            return self

    def execute_serial(self, command):
        messages = self.sim.messagess

        families_messages = []
        for group in self.groups:
            for family in group:
                out_messages = self._processor_groups[0].execute(self.groups, command, messages[group])
                families_messages.append(out_messages)
                messages[group] = []
        messages[('_simulation', 0)] = []
        messages[('_simulation', 0.5)] = []
        for block in families_messages:
            for family_name, family_msgs in block.items():
                messages[family_name].extend(family_msgs)

        self.sim._agents_to_add.extend(messages.pop(('_simulation', 0), []))
        self.sim._agents_to_delete.extend(messages.pop(('_simulation', 0.5), []))

    def execute_parallel(self, command):
        parameters = ((pg, self.groups, command, self.sim.messagess[pgid]) for pgid, pg in enumerate(self._processor_groups))
        out = self.sim.pool.map(execute_wrapper, parameters, chunksize=1)
        #self.sim._agents_to_add.extend(messages.pop(('_simulation', 0), []))
        #self.sim._agents_to_delete.extend(messages.pop(('_simulation', 0.5), []))
        for pgid in range(self.num_managers):
            self.sim.messagess[pgid].clear()
        for out_messages in out:
            for pgid, messages in enumerate(out_messages):
                self.sim.messagess[pgid].extend(messages)

def execute_wrapper(inp):
    # processor_group.execute(self.groups, command, messages[pgid])
    return inp[0].execute(inp[1], inp[2], inp[3])





