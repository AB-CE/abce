import os
import abce
import filecmp as fc
import difflib as dl
import pandas as pd
import numpy as np


class Agent(abce.Agent):
    def go(self):
        self.create('money', 0.1)
        self.i = self.id
        self.r = self.round
        self.log('li', self.i)
        self.log('lr', self.r)
        self.log('l', {'i': self.i, 'r': self.r})


def compare(to_compare, path, message):
    should_be_full = pd.read_csv(to_compare).sort_index(axis=1)
    really_is_full = (pd.read_csv(os.path.join(path, to_compare))
                      .sort_index(axis=1))
    if 'id' in should_be_full.columns:
        should_be_full = (should_be_full
                          .sort_values(by=['id', 'round'], axis=0)
                          .reset_index(drop=True))
        really_is_full = (really_is_full
                          .sort_values(by=['id', 'round'], axis=0)
                          .reset_index(drop=True))
        del should_be_full['index']
        del really_is_full['index']
    assert(should_be_full.shape == really_is_full.shape)
    if not np.isclose(should_be_full, really_is_full).all():
        # finds all lines which are different
        should_be = should_be_full[np.logical_not(
                                   np.min(np.isclose(should_be_full,
                                                     really_is_full),
                                          axis=1))]
        really_is = really_is_full[np.logical_not(
                                   np.min(np.isclose(should_be_full,
                                                     really_is_full),
                                          axis=1))]

        print(to_compare)
        raise Exception(pd.concat([should_be, really_is], axis=1))
    else:
        print(to_compare + ' ' + message + '\tOK')


def main(processes):
    simulation = abce.Simulation(processes=processes)

    simulation.aggregate('agent', variables=['i', 'r'], possessions=['money'])
    simulation.panel('agent', variables=['i', 'r'], possessions=['money'])

    agents = simulation.build_agents(Agent, 'agent', 10, parameters='')

    for r in range(100):
        simulation.advance_round(r)
        agents.do('go')
        agents.aggregate()
        agents.panel()
    simulation.finalize()

    compare('aggregate_agent.csv',
            simulation.path, 'aggregate logging test\t\t')
    compare('aggregate_agent_mean.csv',
            simulation.path, 'aggregate logging test mean\t')
    compare('aggregate_agent_std.csv',
            simulation.path, 'aggregate logging test std\t')

    compare('aggregate_log_agent.csv',
            simulation.path, 'self.log test \t\t\t')
    compare('log_agent.csv', simulation.path, 'self.log test\t\t\t\t')

    compare('aggregate_panel_agent.csv',
            simulation.path, 'aggregated panel logging test\t')
    compare('panel_agent.csv', simulation.path, 'panel logging test\t\t\t')


if __name__ == '__main__':
    main(processes=1)
    main(processes=4)
