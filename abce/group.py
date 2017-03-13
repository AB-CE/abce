class Group(object):
    def __init__(self, sim, groups, name):
        self.sim = sim
        self.groups = groups
        self.name = name
        self.do = self.execute_parallel if sim.processes > 1 else self.execute_serial

    def __add__(self, g):
        return Group(self.sim, self.groups + g.groups, self.name + '+' + g.name)

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
                families_messages.append(family.execute(command, messages[family.name()]))
                messages[family.name()] = []
        messages[('_simulation', 0)] = []
        messages[('_simulation', 0.5)] = []
        for block in families_messages:
            for family_name, family_msgs in block.items():
                messages[family_name].extend(family_msgs)

        self.sim._agents_to_add.extend(messages.pop(('_simulation', 0), []))
        self.sim._agents_to_delete.extend(messages.pop(('_simulation', 0.5), []))

    def execute_parallel(self, command):
        messages = self.sim.messagess
        parameters = ((family, command, messages[family.name()]) for group in self.groups for family in group)
        families_messages = self.sim.pool.map(execute_wrapper, parameters, chunksize=1)
        for group in self.groups:
            for family in group:
                messages[family.name()] = []
        messages[('_simulation', 0)] = []
        messages[('_simulation', 0.5)] = []
        for block in families_messages:
            for family_name, family_msgs in block.items():
                messages[family_name].extend(family_msgs)
        self.sim._agents_to_add.extend(messages.pop(('_simulation', 0), []))
        self.sim._agents_to_delete.extend(messages.pop(('_simulation', 0.5), []))


def execute_wrapper(inp):
    return inp[0].execute(inp[1], inp[2])

