import abce
import platform


class MyAgent(abce.Agent):
    def init(self, name):
        self.name = name

    def say(self):
        return self.name


def main(processes, rounds):
    sim = abce.Simulation()

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


if __name__ == '__main__':
    main(processes=1, rounds=30)
    if (platform.system() != 'Windows' and
            platform.python_implementation() != 'PyPy'):
        main(processes=4, rounds=30)
