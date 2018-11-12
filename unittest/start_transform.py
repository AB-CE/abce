import abcEconomics


class MyAgent(abcEconomics.Agent):
    def init(self):
        self.create('input_good', 10)

    def produce(self):
        assert self['input_good'] == 10 - self.time, (self.time, self['input_good'])
        assert self['output_good'] == 2 * self.time, (self.time, self['output_good'])
        self.transform({'input_good': 1}, {'output_good': 2})

    def all_tests_completed(self):
        print('Test goods.transform:\t\t\tOK')


def main(processes, rounds):
    sim = abcEconomics.Simulation(processes=processes)

    myagents = sim.build_agents(MyAgent, 'myagent', number=2)

    for time in range(rounds):
        sim.time = time
        myagents.produce()

    myagents.all_tests_completed()
    sim.finalize()


if __name__ == '__main__':
    main(processes=1, rounds=5)
    print('Iteration with 1 core finished')
    main(processes=2, rounds=5)
    print('Iteration with multiple processes finished')
