import abce


class Taker(abce.Agent):
    def init(self):
        pass

    def do_take(self):
        self.take(('victim', 0), 'money', self.time)


class Victim(abce.Agent):
    def init(self):
        self.create('money', 10 * 9 * 8 * 7 * 6 * 5 * 4 * 3 * 2)
        self._money = self['money']

    def accept_taking(self):
        for theft in self.get_take('money'):
            self.accept(theft)
        self._money -= self.time
        assert self['money'] == self._money


def main(rounds, processes):
    sim = abce.Simulation(processes=processes)
    takers = sim.build_agents(Taker, 'taker', number=1)
    victims = sim.build_agents(Victim, 'victim', number=1)

    for r in range(10):
        sim.time = r
        takers.do_take()
        victims.accept_taking()
    sim.finalize()


if __name__ == '__main__':
    main(10, 1)
