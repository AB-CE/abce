import abcEconomics
import platform


class MyAgent(abcEconomics.Agent):
    def init(self, name):
        self.name = name

    def say(self):
        return self.name


def main(processes, rounds):
    sim = abcEconomics.Simulation()
    sim.advance_round(0)

    myagents = sim.build_agents(MyAgent, 'myagent', agent_parameters=[{'name': 'me'},
                                                                      {'name': 'you'},
                                                                      {'name': 'him'},
                                                                      {'name': ('firm', 0)}])

    names = ['me', 'you', 'him', ('firm', 0)]
    for name in names:
        assert list(myagents.by_name(name).say()) == [name], (
            list(myagents.by_name(name).say()), [name])

    assert list(myagents.by_name(name).say()) == [name], (
        list(myagents.by_names(names).say()), names)
    sim.finalize()


if __name__ == '__main__':
    main(processes=1, rounds=30)
    if (platform.system() != 'Windows' and
            platform.python_implementation() != 'PyPy'):
        main(processes=2, rounds=30)
