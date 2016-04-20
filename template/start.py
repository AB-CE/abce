from __future__ import division
from firm import Firm
from household import Household
from abce import Simulation, gui

simulation_parameters = {'name', 'name',
                         'rounds': 500,
                         'firms': 5,
                         'households': 5}

@gui(simulation_parameters)
def main():
        s = Simulation(simulation_parameters)
        action_list = [
        repeat([
            ('firm', 'one'),
            ('household', 'two'),
            ], simulation_parameters['trade_repetitions']),
            ('all', 'three')
        ]
        s.add_action_list(action_list)

        s.build_agents(Firm,
                       simulation_parameters['firms'],
                       parameters=simulation_parameters)
        s.build_agents(Household,
                       simulation_parameters['household'],
                       parameters=simulation_parameters)

        s.declare_round_endowment(
                    resource='labor_endowment',
                    productivity=1,
                    product='labor'
        )
        s.declare_perishable(good='labor')

        s.panel_data('household')
        s.panel_data('firm')

        s.run()

if __name__ == '__main__':
    main()

