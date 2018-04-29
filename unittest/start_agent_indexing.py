import abce


class MyAgent(abce.Agent):
    def init(self, name):
        self.name = name

    def say(self):
        return self.name


sim = abce.Simulation()

myagents = sim.build_agents(MyAgent, 'myagent', agent_parameters=[{'name': 'me'},
                                                                  {'name': 'you'},
                                                                  {'name': 'him'},
                                                                  {'name': ('firm', 0)}])


for name in ['me', 'you', 'him', ('firm', 0)]:
    assert list(myagents[name].say()) == [name], (list(myagents[name].say()), [name])
