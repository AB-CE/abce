import platform
import csv
import abcEconomics
try:
    from math import isclose
except ImportError:
    def isclose(a, b):
        return a - 0.000001 < b < a + 0.000001


class Agent(abcEconomics.Agent):
    def init(self, name):
        self.name = name

    def go(self):
        self.create('money', 0.1)
        self.i = self.id
        self.r = self.time[0] + 10 * self.time[1]
        self.log('li', self.i)
        self.log('lr', self.r)
        self.log('l', {'i': self.i, 'r': self.r})


def compare(to_compare, path, message, processes):

    the_path = (path + '/' + to_compare)
    if platform.system() == 'Windows':  # windows compatibility
        the_path = the_path[the_path.find('/') + 1:]

    with open(to_compare, 'r') as generatedf:
        generated = {}
        for row in csv.DictReader(generatedf):
            try:
                generated[(row['round'], row['name'])] = row
            except KeyError:
                generated[row['round']] = row
    with open(the_path, 'r') as orginialf:
        orginial = {}
        for row in csv.DictReader(orginialf):
            try:
                orginial[(row['round'], row['name'])] = row
            except KeyError:
                orginial[row['round']] = row
    for row in generated:
        for key in generated[row]:
            if key != 'index':
                if generated[row][key] != orginial[row][key]:
                    assert isclose(float(generated[row][key]), float(orginial[row][key])), (
                        key, generated[row][key], orginial[row][key])
    for row in orginial:
        for key in orginial[row]:
            if key != 'index':
                if generated[row][key] != orginial[row][key]:
                    assert isclose(float(generated[row][key]), float(orginial[row][key])), (
                        key, generated[row][key], orginial[row][key])


def main(processes, rounds):
    simulation = abcEconomics.Simulation(name='logging_test_friendly_names', processes=processes)

    agents = simulation.build_agents(Agent, 'friendly_agent',
                                     agent_parameters=[{'name': 'A'}, {'name': 'Davoud'}, {'name': "fred"}, {'name': "F12"}])

    for rnd in range(10):
        for r in range(10):
            simulation.advance_round((r, rnd))
            agents.go()
            agents.agg_log(variables=['i', 'r'], goods=['money'])
            agents.panel_log(variables=['i', 'r'], goods=['money'])
    simulation.finalize()

    compare('aggregated_friendly_agent.csv',
            simulation.path, 'aggregated logging test\t\t',
            processes)
    compare('aggregate_friendly_agent.csv',
            simulation.path, 'aggregate logging test\t\t',
            processes)
    compare('panel_friendly_agent.csv',
            simulation.path, 'aggregate logging test mean\t',
            processes)


if __name__ == '__main__':
    main(processes=1, rounds=None)
    if (platform.system() != 'Windows' and platform.python_implementation() != 'PyPy'):
        main(processes=2, rounds=None)
