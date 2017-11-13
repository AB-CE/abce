class SingleProcess(object):
    def __init__(self):
        self.agents = {}

    def new_group(self, group):
        self.agents[group] = []

    def append(self, agent, group, id):
        self.agents[group].append(agent)

    def __getitem__(self, group):
        return self.agents[group]

