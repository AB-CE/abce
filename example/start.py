#ABMm_0.0.1 Do NOT change or delete any #ABMm... tags!!! Always write
#between them, if you have no very good reason not to do so.
"""
To write a SLAPP model there are three steps:
(1) define the Agent in Agent.py and
(2) the action groups calling the Agents in ModelSwarm.py. Further
(3) define the sequence of actions in ModelSwarm.py.
(4) parameter in parameter.csv and world.py
Further instructions contained in the files.
"""
import sys
sys.path.append('../lib')
import world
from firm import Firm
from household import Household
from nature import Nature
from abce_common import agent_name, group_address

for parameter in world.read_parameters('world_parameters.csv'):
    action_list = [
        ('Nature', 'assign'),
        ('all', 'recieve_connections'),
        ('Household', 'offer_capital'),
        ('Firm', 'buy_capital'),
        ('Household', 'offer_labor'),
        ('Firm', 'hire_labor'),
        ('Household', 'accept_job_offer'),
        'before_production',
        ('Firm', 'production'),
        ('Firm', 'sell_good'),
        ('Household', 'buy_good'),
        'after_sales_before_consumption',
        ('Household', 'consumption')
        ]
    w = world.World(parameter)
    w.add_action_list(action_list)
    #w.add_action_list_from_file()


    w.build_agents(Firm, number='number_of_firms')
    w.build_agents(Household, number='number_of_households')
    w.build_agents(Nature, 1)


    w.declare_resource(resource='labor_endowment', productivity=1000, product='labor')
    w.declare_resource(resource='capital_endowment', productivity=1000, product='capital')
    w.follow_agent('Household', 0)
    w.follow_agent('Firm', 0)

    w.panel_db('Household', command='after_sales_before_consumption')
    w.panel_db('Firm', command='after_sales_before_consumption')
    w.panel_db('Firm', command='before_production')
    w.run()

