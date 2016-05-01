from __future__ import division
from agent import Agent
from abce import Simulation, gui

simulation_parameters = {'name': 'datetimedemonstration',
                         'rounds': 50,}

def main(simulation_parameters):
        simulation = Simulation(rounds=simulation_parameters['rounds'])
        action_list = [('agent', 'wednessday', lambda date: date.weekday() == 2),
                       ('agent', 'first', lambda date: date.day == 1),
                       ('agent', 'newyearseve', lambda date: date.month == 12 and date.day == 31),
                       ('agent', 'firstfriday', lambda date: date.day <= 7 and date.weekday() == 4),
                       ('agent', 'fiveteens', lambda date: date.month == 15),
                       ('agent', 'everythreedays', lambda date: date.toordinal() % 3 == 0)]
        simulation.add_action_list(action_list)
        simulation.declare_calendar(2000, 1, 1)
        simulation.build_agents(Agent, 'agent', number=1)


        simulation.run()


if __name__ == '__main__':
    main(simulation_parameters)

