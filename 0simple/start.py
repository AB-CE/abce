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
from agent import Agent

for parameter in world.read_parameters('parameter.csv'):
    w = world.World(parameter)
    w.build_agents(Agent, 'agent', 3)
    w.build_agents(Agent, 'bgent', 3)
    w.run()
