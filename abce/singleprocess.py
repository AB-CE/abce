class SingleProcess(object):
    def __init__(self):
        self.agents = {}

    def new_group(self, group):
        self.agents[group] = []

    def append(self, agent, group, id):
        self.agents[group].append(agent)

    def get_agents(self, groups, ids):
        for group, iss in zip(groups, ids):
            for i in iss:
                if i is not None:
                    yield self.agents[group][i]

    def get(self, group, id):
        return self.agents[group][id]
