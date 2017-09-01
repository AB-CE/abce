import platform
from filecmp import cmp
import csv
import abce



class Agent(abce.Agent):
    def go(self):
        self.create('money', 0.1)
        self.i = self.id
        self.r = self.round
        self.log('li', self.i)
        self.log('lr', self.r)
        self.log('l', {'i': self.i, 'r': self.r})


def compare(to_compare, path, message, processes):
    the_path = (path + '/' + to_compare)
    if platform.system() == 'Windows':  # windows compatibility
        the_path = the_path[the_path.find('/') + 1:]
    if processes == 1:
        assert cmp(to_compare, the_path)
    else:
        with open(to_compare, 'r') as generatedf:
            generated = {}
            for row in csv.DictReader(generatedf):
                try:
                    generated[(row['round'], row['id'])] = row
                except KeyError:
                    generated[row['round']] = row
        with open(the_path, 'r') as orginialf:
            orginial = {}
            for row in csv.DictReader(orginialf):
                try:
                    orginial[(row['round'], row['id'])] = row
                except KeyError:
                    orginial[row['round']] = row
        for row in generated:
            for key in generated[row]:
                generated[row][key] == orginial[row][key], (key, generated[row][key], orginial[row][key])
        for row in orginial:
            for key in orginial[row]:
                generated[row][key] == orginial[row][key], (key, generated[row][key], orginial[row][key])






def main(processes):
    simulation = abce.Simulation(processes=processes)

    agents = simulation.build_agents(Agent, 'agent', 10, parameters='')

    for rnd in range(100):
        simulation.advance_round(rnd)
        agents.go()
        agents.agg_log(variables=['i', 'r'], possessions=['money'])
        agents.panel_log(variables=['i', 'r'], possessions=['money'])
    simulation.finalize()

    if platform.system() == 'Windows':
        simulation.path = simulation.path.replace('/', '\\')

    compare('aggregated_agent.csv',
            simulation.path, 'aggregated logging test\t\t',
            processes)
    compare('aggregate_agent.csv',
            simulation.path, 'aggregate logging test\t\t',
            processes)
    compare('panel_agent.csv',
            simulation.path, 'aggregate logging test mean\t',
            processes)


if __name__ == '__main__':
    main(processes=1)
    main(processes=4)
