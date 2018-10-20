import platform
import abcEconomics


class Returner(abcEconomics.Agent):
    def init(self):
        pass

    def returnit(self):
        return self.name, self.id, (0, 1, 2, 3), self.time


class Getter(abcEconomics.Agent):
    def init(self):
        pass

    def getit(self, zeug):
        assert set(zeug) == set([(('returner', 0), 0, (0, 1, 2, 3), self.time),
                                 (('returner', 1), 1, (0, 1, 2, 3), self.time),
                                 (('returner', 2), 2, (0, 1, 2, 3), self.time)]), list(zeug)

    def method(self, a, b, c, d, e, f):
        assert a == 'a'
        assert b == 'b'
        assert c == 'c'
        assert d == 'd'
        assert e == 'e'
        assert f == 'f'


def main(processes, rounds):
    sim = abcEconomics.Simulation(processes=processes)

    returners = sim.build_agents(Returner, 'returner', number=3)
    getters = sim.build_agents(Getter, 'getter', number=1)

    for y in range(rounds):
        sim.advance_round(y)
        ret = returners.returnit()
        getters.getit(ret)
        getters.method('a', 'b', 'c', d='d', f='f', e='e')
    sim.finalize()
    print('Returning tested \t\t\t\t\t\tOK')
    print('Calling with parameters tested \t\t\t\t\tOK')


if __name__ == '__main__':
    main(processes=1, rounds=30)
    if (platform.system() != 'Windows' and
            platform.python_implementation() != 'PyPy'):
        main(processes=2, rounds=30)
