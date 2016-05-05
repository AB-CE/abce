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
        action_list = [('killer', 'kill'),
                       ('agent', 'am_I_dead'),
                       ('killer', 'send_message'),
                       ('agent', 'aggregate'),
                       ('agent', 'panel')]  # this instructs ABCE to save panel data as declared below
        simulation.add_action_list(action_list)

        simulation.declare_round_endowment(resource='labor_endowment',
                                           units=1,
                                           product='labor'
        )
        simulation.declare_perishable(good='labor')

        simulation.aggregate('agent', possessions=[], variables=['count'])
        simulation.panel('agent', possessions=[], variables=['idn'])

        simulation.build_agents(Agent, 'agent',
                       number=simulation_parameters['agents'],
                       parameters=simulation_parameters)
        simulation.build_agents(Killer, 'killer',
                       number=1,
                       parameters=simulation_parameters)


        simulation.run()
        simulation.graphs()

if __name__ == '__main__':
    main(simulation_parameters)

