from __future__ import division
from agent import Agent
from killer import Killer
from abce import Simulation, gui

simulation_parameters = {'name': 'name',
                         'rounds': 100,
                         'firms': 5,
                         'agents': 100}

# commend out simulation.graphs() and uncomment
# this line to run the simulation with a Graphical
#@gui(simulation_parameters) # User Interface


def main(simulation_parameters):
    simulation = Simulation(rounds=simulation_parameters['rounds'])
    simulation.declare_round_endowment(resource='labor_endowment',
                                       units=1,
                                       product='labor')
    simulation.declare_perishable(good='labor')

    simulation.aggregate('agent', possessions=[], variables=['count'])
    simulation.panel('agent', possessions=[], variables=['idn'])

    agents = simulation.build_agents(Agent, 'agent',
                                     number=simulation_parameters['agents'],
                                     parameters=simulation_parameters)
    killers = simulation.build_agents(Killer, 'killer',
                                      number=1,
                                      parameters=simulation_parameters)
    for r in simulation.next_round():
        killers.do('kill')
        agents.do('am_I_dead')
        killers.do('send_message')
        agents.do('aggregate')
        agents.do('panel')

    simulation.graphs()


if __name__ == '__main__':
    main(simulation_parameters)
