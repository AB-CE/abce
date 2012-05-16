#ABMm_0.0.1 Do NOT change or delete any #ABMm... tags!!! Always write
#between them, if you have no very good reason not to do so.
"""
To write a ABCE model there are three steps::

 (1) define agent in AgentName.py using the 'Agent.py' prototype
 (2) modify this file
    (a) import agents
    (b) define action_list below [('which_agent', 'does_what'), ...]
    (c) define parameter suchs as the number_of_each_agent_type in parameter.csv
    (d) build_agents
    (e) declare some goods as resources

Further instructions contained in the files.
"""
import sys
sys.path.append('../lib')
import world
from firm import Firm
from household import Household

for parameter in world.read_parameter('world_parameters.csv'):
    action_list = [
    ('household', 'recieve_connections'),
    ('household', 'offer_capital'),
    ('firm', 'buy_capital'),
    ('household', 'search_work'),
    ('firm', 'hire_labor'),
    ('firm', 'production'),
    'after_sales_before_consumption'
    ]
    w = world.World(parameter)
    w.add_action_list(action_list)
    w.build_agents(Firm, 'firm', 'number_of_firms')
    w.build_agents(Household, 'household', 'number_of_households')

    w.declare_resource(resource='labor_endowment', productivity=1, product='labor')
    w.declare_resource(resource='capital_endowment', productivity=1, product='capital')

    w.panel_db('firm', command='after_sales_before_consumption')

    w.run()

