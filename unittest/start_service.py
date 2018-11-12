import abcEconomics


class Endowment(abcEconomics.Agent):
    def init(self, rounds):
        self.last_round = rounds - 1
        self.labor_endowment = 0

    def Iconsume(self):
        assert self['labor'] == 5 * self.time, (self.time, 5 * self.time, self['labor'])
        self.labor_endowment = self.time + 1

    def all_tests_completed(self):
        print('Test s.refresh_services:\t\t\tOK')


def main(processes, rounds):
    s = abcEconomics.Simulation(processes=processes, name='unittest')

    endowment = s.build_agents(Endowment, 'endowment', 2, rounds=rounds)

    for r in range(rounds):
        s.time = r
        endowment.refresh_services('labor', derived_from='labor_endowment', units=5)
        endowment.Iconsume()
    endowment.all_tests_completed()
    s.finalize()


if __name__ == '__main__':
    main(processes=1, rounds=5)
    print('Iteration with 1 core finished')
    main(processes=2, rounds=5)
    print('Iteration with multiple processes finished')
