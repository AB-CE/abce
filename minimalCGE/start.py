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

for parameter in world.read_parameter('parameter.csv'):
    action_list = [
        ('nature', 'assign'),
        ('all', 'recieve_connections'),
        ('household', 'offer_capital'),
        ('firm', 'buy_capital'),
        ('household', 'offer_labor'),
        ('firm', 'hire_labor'),
        ('household', 'accept_job_offer'),
        'before_production',
        ('firm', 'production'),
        ('firm', 'sell_good'),
        ('household', 'buy_good'),
        'after_sales_before_consumption',
        ('household', 'consumption')
        ]
    w = world.World(parameter)
    w.add_action_list(action_list)

    w.build_agents(Firm, 'firm', 'number_of_firms')
    w.build_agents(Household, 'household', 'number_of_households')
    w.build_agents(Nature, 'nature', 1)


    w.declare_resource(resource='labor_endowment', productivity=1000, product='labor')
    w.declare_resource(resource='capital_endowment', productivity=1000, product='capital')
    for i in range(parameter['number_of_households']):
        if i % 50 == 0:
            w.follow_agent('household', i)
    for i in range(parameter['number_of_firms']):
        if i % 5 == 0:
            w.follow_agent('firm', i)

    w.start_db('household', command='after_sales_before_consumption')
    w.start_db('firm', command='after_sales_before_consumption')
    w.start_db('firm', command='before_production')
    w.run()

