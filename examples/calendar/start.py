from __future__ import division
from agent import Agent
from abce import Simulation, gui

simulation_parameters = {'name': 'datetimedemonstration',
                         'rounds': 50,}

def main(simulation_parameters):
        simulation = Simulation(rounds=simulation_parameters['rounds'])
        simulation.declare_calendar(2000, 1, 1)
        simulation.panel('agent', possessions=['money'])
        simulation.aggregate('agent', possessions=['labor'])
        agents = simulation.build_agents(Agent, 'agent', number=1)

        for r in simulation.next_round():
            date = simulation._round
            if date.weekday() == 2:
                agents.do('wednessday')
            if date.day == 1:
                agents.do('first')
            if date.month == 12 and date.day == 31:
                agents.do('newyearseve')
            if date.day <= 7 and date.weekday() == 4:
                agents.do('firstfriday')
            if date.month == 15:
                agents.do('fiveteens')
            if date.toordinal() % 3 == 0:
                agents.do('everythreedays')
            agents.do('panel')
            agents.do('aggregate')

        simulation.graphs()


if __name__ == '__main__':
    main(simulation_parameters)

