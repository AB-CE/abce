from collections import defaultdict


class SingleProcess(object):
    def __init__(self):
        self.agents = defaultdict(list)

    def append(self, agent, group, id):
        self.agents[group].append(agent)

    def __getitem__(self, groups):
        return self.agents[groups]
