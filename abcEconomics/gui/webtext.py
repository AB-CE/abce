""" Describes abcEconomics on GUI, if no other text is given"""


abcEconomicsdescription = """ (drag me)
<h1>abcEconomics a Python based modeling library for economic simulations.</h1>
For simulations of trade, production and consumption, abcEconomics comes with stan
dard functions that implement these kinds of interactions and actions. The
modeler only has to implement the logic and decisions of an agent; abcEconomics takes
care of all exchange of goods and production and consumption.







One special feature of abcEconomics is that goods have the physical properties of


goods in reality. In other words if agent A gives a good to agent B, then -
 unlike information - agent B receives the good and agent B does not have the
 good anymore. That means that agents can trade, produce or consume a good.
 The ownership and transformations (production or consumption) of goods are
 automatically handled by the platform.







abcEconomics models are programmed in standard Python, stock functions of agents a


re inherited from archetype classes (Agent, Firm or Household). The only no
t-so-standard Python is that agents are executed in parallel by the
Simulation class (in start.py).







abcEconomics allows the modeler to program agents as ordinary Python class-objects


, but run the simulation on a multi-core/processor computer. It takes no ef
fort or intervention from the modeller to run the simulation on a multi-core
processor production, consumption, trade, communication and similar
functions are automatically handled by the platform. The modeler only needs
to instruct abcEconomics, which automatically executes the specific functions.







abcEconomics is a scheduler [1] and a set of agent classes. According to the sched


ule the simulation class calls - each sub-round - agents to execute some ac
tions. Each agent executes these actions using some of the build-in
functions, such as trade, production and consumption of abcEconomics. The agents
can use the full set of commands of the Python general purpose language.







The audience of abcEconomics are economists that want to model agent-based models


of trade and production. It is especially geared towards simulations that a
re similar to standard economic models like general or partial equilibrium
models [2]. What is more abcEconomics is especially designed to make writing the
simulation and the execution fast. Therefore models can be developed in an
interlinked process of running and rewriting the simulation.







abcEconomics uses Python - a language that is especially beginner friendly, but al

so easy to learn for people who already know object oriented programming la
nguages such as Java, C++ or even MATLAB. Python allows simple, but fully
functional, programming for economists. What is more Python is readable even
for non Python programmers.
<h2> <a href="http://abcEconomics.readthedocs.io/en/master/">Find the Documentatio
n at readthedocs</a> </h2>"""
