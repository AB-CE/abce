import itertools


class SingleProcess(object):
    def __init__(self):
        self.agents = {}

    def new_group(self, group):
        self.agents[group] = []

    def append(self, agent, group, id):
        self.agents[group].append(agent)

    def __getitem__(self, groups):
        return itertools.chain(*(self.agents[group] for group in groups))

    def get(self, group, id):
        return self.agents[group][id]
