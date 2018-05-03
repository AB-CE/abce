import abce
import platform


class MyAgent(abce.Agent):
    def init(self):
        pass

    def say(self):
        return self.id


def main(processes, rounds):
    sim = abce.Simulation()

    myagents = sim.build_agents(MyAgent, 'myagent', number=5)

    for id in range(5):
        assert list(myagents[id].say()) == [id], (list(myagents[id].say()), [id])


if __name__ == '__main__':
    main(processes=1, rounds=30)
    if (platform.system() != 'Windows' and
            platform.python_implementation() != 'PyPy'):
        main(processes=4, rounds=30)
