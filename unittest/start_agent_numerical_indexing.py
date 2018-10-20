import abcEconomics
import platform


class MyAgent(abcEconomics.Agent):
    def init(self):
        pass

    def say(self):
        return self.id


def main(processes, rounds):
    sim = abcEconomics.Simulation()
    sim.advance_round(0)

    myagents = sim.build_agents(MyAgent, 'myagent', number=5)

    for id in range(5):
        assert list(myagents[id].say()) == [id], (list(myagents[id].say()), [id])
    sim.finalize()


if __name__ == '__main__':
    main(processes=1, rounds=30)
    if (platform.system() != 'Windows' and
            platform.python_implementation() != 'PyPy'):
        main(processes=2, rounds=30)
