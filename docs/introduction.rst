.. role:: raw-tex(raw)
    :format: latex html


Design
======

abcEconomics's first design goal is that, code can be rapidly written,
to enable a modeler to quickly write down
code and quickly explore different alternatives of a model.

Execution speed is a secondary concern to the goal of rapid development.
Execution speed is achieved by making use of multiple-cores/processors
and using C++ for background tasks or using pypy.

Secondly, the modeler can concentrate on programming the behavior of the agents and
the specification of goods, production and consumption function.
The functions for economic simulations such as production, consumption,
trade, communication are provided and automatically performed by the platform.

Python has also been chosen as a programming language, because of
it's rich environment of standard libraries. Python for example
comes with a stock representation of agents in a spacial world,
which allow the modeler to model a spatial model.

Python is especially beginner friendly, but also
easy to learn for people who already know object oriented programming
languages such as Java, C++ or even MATLAB. abcEconomics uses C++, to handle
background tasks to increase speed.
Python allows simple, but fully functional, programming for economists.
What is more Python is readable even for non Python programmers.

Python is a language that lends itself to writing of code fast, because it
has low overhead. In Python variables do not have to be declared, garbage
does not have to be collected and classes have no boiler-plate code.

Python, is slower than Java or C, but its reputation for slow speed is usually
exaggerated. Various packages for numerical calculations and optimization such as numpy and scipy offer
the C like speed to numerical problems. Contrary to the common belief
Python is not an interpreted language. Pypy even provides a just in time
complier Python is compiled to bytecode and than executed. abcEconomics allows
to parallelize the code and gain significant speed advantage over
single-threaded code, that does not make use of the speed advantage of
multi-core or multi-processor computers.

abcEconomics 0.6 supports Python 3.

.. [#interpreter] Python is often falsely believe to be an interpreted language

For the simulated problem all agents are executed in parallel. This is
achieved by randomizing the arrival of messages and orders between sub-rounds.
For example if in one sub-round all agents make offers and in the next
sub-round all agents receive and answer the offers, the order in which
the agents receive is random, as if the agent's in the round before
would make offers in a random order.

Differences to other agent-based modeling platforms
---------------------------------------------------

We identified several survey articles as well as
a quite complete overview of agent-based modeling software
on Wikipedia. [Serenko2002]_, [Allan2010]_
[Societies2009]_, [Tobias2004]_, [Railsback2006]_,
[abmcomparisonWikipedia2013]_. The articles
'Tools of the Trade' by Madey and Nikolai [Societies2009]_
and 'Survey of Agent Based Modelling and Simulation Tools' by Allan  [Allan2010]_
attempt to give a complete overview
of agent-based modelling platforms/frameworks. The Madey and Nikolai paper
categorizes the abm-platforms according
to several categories. (Programming Language, Type of License,
Operating System and Domain). According to this article, there
is only one software platform which aims at the specific
domain of economics: JASA. But JASA is a modeling platform
that aims specifically at auctions.
Wikipedia [abmcomparisonWikipedia2013]_ lists JAMEL
as an economic platform, but JAMEL a is closed source and
an non-programming platform. The 'Survey of Agent Based Modelling and Simulation Tools'
by Allan [Allan2010]_ draws
our attention to LSD, which, as it states, is rather a system dynamic,
than an agent-based modeling platform. We conclude that
there is a market for a domain specific language for economics.

While the formerly mentioned modeling platforms aim to give a
complete overview, 'Evaluation of free Java - libraries for
social scientific agent based simulation' [Tobias2004]_
by Tobias and Hoffman
chooses to concentrate on a smaller number of simulation packages.
Tobias and Hoffman discuss: RePast, Swarm, Quicksilver, and VSEit.
We will follow this approach and concentrate on a subset of
ABM models. First as economics is a subset of social science we
dismiss all platforms that are not explicitly targeted at
social science. The list of social science platforms according
to [Societies2009]_ Madey and Nikolai is:
AgentSheets, LSD, FAMOJA, MAML, MAS-SOC,  MIMOSE, NetLogo, Repast
SimBioSys, StarLogo, StarLogoT, StarLogo TNG, Sugarscape, VSEit
NetLogo and  Moduleco.
We dismiss some of these frameworks/platforms:

AgentSheets,
    because it is closed source and not 'programable'
LSD,
    because it is a system dynamics rather than an agent-based modeling environment
MAML,
    because it does not use a standard programming language, but it is it's own.
MAS-SOC,
    because we could not find it in the Internet and its documentation
    according to [Allan2010]_ is sparse.
MIMOSE,
    is an interesting language, but we will not analyze as it is based on a completely different
    programming paradigm, functional programming, as opposed to object-oriented
    programming.
SimBioSys,
    because it has according to Allan [Allan2010]_ and our research  a sparse documentation.
StarLogo, StarLogoT, StarLogo TNG,
    because they have been superseded by NetLogo
Moduleco,
    because it has  according to Allan [Allan2010]_ and our research a sparse documentation.
    Further, it appears not to be updated since roughly 2001

We will concentrate on the most widely used ABM frameworks/platforms: MASON, NetLogo, Repast.

General differences to other agent-based modeling platforms
-----------------------------------------------------------

First of all abcEconomics is domain specific, that enables it to provide
the basic functions such as production, consumption, trade and
communication as fully automated stock methods.
Because any kind of agent interaction (communication and exchange of
goods) is handled automatically abcEconomics, it can run the agents (virtually)
parallel and run simulations on multi-core/processor systems without
any intervention by the modeler.

The second biggest difference between abcEconomics and other platforms
is that abcEconomics introduces the physical good as an ontological object in
the simulation. Goods can be exchanged and transformed. abcEconomics handles
these processes automatically, so that for the model a physical good
behaves like a physical good and not like a message. That means that
if a good is transfered between two agents the first agent does not
have this good anymore, and the second agent has it now. Once, for
example, two agents decide to trade
a good abcEconomics makes sure that the transaction is cleared between
the two agents.

Thirdly, abcEconomics is just a scheduler that schedules the actions of
the agents and a python base class that enables the agent to
produce, consume, trade and communicate. A model written
in abcEconomics, therefore is standard Python code and the modeler can make
use of the complete Python language and the Python language environment.
This is a particular useful feature because Python comes with about 30.000 [#30000]_
publicly available packages, that could be used in abcEconomics. Particularly
useful packages are:

pybrain
    a neural network package
numpy
    a package for numerical computation
scipy
    a package for numerical optimization and statistical functions
sympy
    a package for symbolic manipulation
turtle
    a package for spacial representation ala NetLogo

Fourth, many frameworks such as FLAME, NetLogo, StarLogo, Ascape
and SugarScape and, in a
more limited sense, Repast are designed with spacial representation in mind.
For abcEconomics a spacial representation is possible, but not a design goal.
However, since agents in abcEconomics are ordinary Python objects, they can use
python modules such as python-turtle and therefore gain a spacial
representation much like NetLogo. This does by no means mean that
abcEconomics could not be a good choice for a problem where the spacial
position plays a role. If for example the model has different
transport costs or other properties according to the geographical
position of the agents, but the agent's do not move or the movement
does not have to be represented graphically, abcEconomics could still be a
good choice.

Difference to MASON
```````````````````

Masons is a single-threaded discrete event platform that is intended
for simulations of social, biological and economical systems.
[Luke]_. Mason is a platform that was explicitly designed with the goal of
running it on large platforms. MASON distributes a large number
of single threaded simulations over deferent computers or processors.
abcEconomics on the other hand is multi-threaded it
allows to run agents in parallel. A single run of a simulation
in MASON is therefore not faster on a computing cluster than
on a potent single-processor computer. abcEconomics on the other hand
uses the full capacity of multi-core/processor systems for
a single simulation run. The fast
execution of a model in abcEconomics allow a different software
development process, modelers can 'try' their models while they
are developing and adjust the code until it works as desired.
The different nature of both
platforms make it necessary to implement a different event
scheduling system.

Mason is a discrete event platform. Events can be scheduled by the
agents. abcEconomics on the other hand is scheduled -
it has global list of sub-rounds that establish the sequence
of actions in every round. Each of these sub-rounds lets a
number of agents execute the same actions in parallel.

MASON, like Repast Java is based on Java, while abcEconomics is
based on Python, the advantages have been discussed before.

Difference to NetLogo
`````````````````````

Netlogo is a multi-agent programming language, which is part of
the Lisp language family. Netlogo is interpreted.
[Tisue2004]_ Python on the
other hand is a compiled [#compiled]_ general programming language.
Consequently it is faster than NetLogo.

Netlogo's most prominent feature are the turtle agents. To
have turtle agents in abcEconomics, Python's turtle library has to be
used. The graphical representation of models is therefore not
part of abcEconomics, but of Python itself, but needs to be included by
the modeler.

One difference between Netlogo and abcEconomics is that it has the
concept of the observer agent, while in abcEconomics the simulation
is controlled by the simulation process.

Difference Repast
`````````````````

Repast is a modeling environment for social science. It was
originally conceived as a Java recoding of SWARM.
[Collier]_ [NORTH2005]_ Repast
comes in several flavors: Java, .Net, and a Python like
programming language. Repast has been superseded by
Repast Symphony which maintains all functionality, but
is limited to Java. Symphony has a point and click
interface for simple models. [NORTH2005a]_

Repast does allow static and dynamic scheduling.
[Collier]_. abcEconomics,
does not (yet) allow for dynamic scheduling. In abcEconomics, the
order of actions - or in abcEconomics language order of sub-rounds -
is fixed and is repeated for every round. This however is not
as restrictive as it sounds, because in any sub-round an
agent could freely decide what he does.

The advantage of the somehow more limited implementation of
abcEconomics is ease of use. While in Repast it is necessary to
subclass the scheduler in abcEconomics it is sufficient to specify
the schedule and pass it the Simulation class.

Repast is vast, it contains 210 classes in 9 packages
[Collier]_. abcEconomics, thanks to its limited
scope and Python, has only 6 classes visible to the
modeler in a single package.



.. [#30000] https://pypi.python.org/

Physical Goods
--------------

Physical goods are at the heart of almost every economic model.
The core feature and main difference to other ABM platforms is the
implementation of physical goods. In contrast
to information or messages, sharing a good means having less of it. In other
words if agent A gives a good to agent B then agent A does not have this good
anymore. On of the major strength of abcEconomics is that this is automatically handled.

In abcEconomics goods can be created, destroyed, traded, given or changed through
production and consumption. All these functions are implemented in abcEconomics and
can be inherited by an agent as a method. These functions are automatically handled by
abcEconomics upon decision from the modeler.

Every agent in abcEconomics must inherit from the abcEconomics.Agent class. This gives the
agent a couple of stock methods: create, destroy, trade and give. Create and
destroy create or destroy a good immediately. Because trade and give involve
a form of interaction between the agents they run over several sub-rounds.
Selling of a good for example works like this:

- Sub-round 1. The first agent offers the goods.
       The good is automatically subtracted from the agents possessions, to avoid double selling.
- Sub-round 2. The counter agent receives the offer. The agent can
    1. accept:
       the goods are added to the counter part's possessions. Money is subtracted.
    2. reject (or equivalently ignore):
       Nothing happens in this sub-round
    3. partially accept the offer:
       The partial amount of goods is added to the counter part's possessions. Money is subtracted.
- Sub-round 3. In case of
    1. acceptance, the money is credited
    2. rejection the original good is re-credited
    3. partial acceptance the money is credited and
       the unsold part of the good is re-credited.




.. [#compiled]  Python contrary to the common believe is compiled to bytecode similar to Java's compilation to bytecode.



