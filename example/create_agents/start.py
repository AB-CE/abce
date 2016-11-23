from __future__ import division
from firm import Firm
from household import Household
from messenger import Messenger
from abce import Simulation, gui

simulation_parameters = {'name': 'name',
                         'rounds':  10,
                         'firms': 1,
                         'households': 0}

                             # commend out simulation.graphs() and uncomment
                             # this line to run the simulation with a Graphical
#@gui(simulation_parameters) # User Interface
def main(simulation_parameters):
        simulation = Simulation(rounds=simulation_parameters['rounds'])

        simulation.declare_round_endowment(resource='labor_endowment',
                                           units=1,
                                           product='labor')

        simulation.declare_perishable(good='labor')

        simulation.aggregate('household', possessions=[],  # put a list of household possessions to track here
                                      variables=['count']) # put a list of household possessions to track here

        simulation.aggregate('firm', possessions=[],  # put a list of household possessions to track here
                                      variables=['count']) # put a list of household possessions to track here

        firms = simulation.build_agents(Firm, 'firm',
                       number=simulation_parameters['firms'],
                       parameters=simulation_parameters)

        households = simulation.build_agents(Household, 'household',
                       number=simulation_parameters['households'],
                       parameters=simulation_parameters)

        messengers = simulation.build_agents(Messenger, 'messenger', 1)

        for r in simulation.next_round():
            messengers.do('messaging')
            (firms+households).do('receive_message')
            firms.do('add_household')
            firms.do('add_firm')
            firms.do('print_id')
            households.do('print_id')
            # this instructs ABCE to save panel data as declared below
            (firms+households).do('aggregate')
        simulation.graphs()

if __name__ == '__main__':
    main(simulation_parameters)

