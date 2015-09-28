.. role:: raw-tex(raw)
    :format: latex html


Introduction
------------

ABCE is a Python based modeling platform for economic simulations.
For simulations of trade, production and consumption, ABCE comes
with standard functions that implement these kinds of interactions
and actions. The modeler only has to implement
the logic and decisions of an agent; ABCE takes care of all exchange
of goods and production and consumption.

One special feature of ABCE is that goods have the physical properties of
goods in reality. In other words if agent A gives a good to agent B, then
- unlike information - agent B receives the good and agent B does not have
the good anymore. That means that agents can trade, produce or consume a good.
The ownership and transformations (production or consumption) of goods are
automatically handled by the platform.

ABCE has been designed for economic problems where spacial representation
is not important or the spacial position of the agents is (largely) fixed.
Therefore instead of representing the simulation graphically, ABCE collects
data of the simulation and outputs it ready to use for R and Excel.

ABCE models are programmed in standard Python, stock functions of agents
are inherited from archetype classes (Agent, Firm or Household). The only
not-so-standard Python is that agents are executed in parallel by the
Simulation class (in start.py).

ABCE allows the modeler to program agents as ordinary Python class-objects,
but run the simulation on a multi-core/processor computer. It takes no
effort or intervention from the modeller to run the simulation on a
multi-core processor production,
consumption, trade, communication and similar functions are automatically
handled by the platform. The modeler only needs to instruct ABCE, which
automatically executes the specific functions.

ABCE is a scheduler [#scheduler]_ and a set of agent classes.
According to the schedule the simulation class calls - each sub-round - agents
to execute some actions. Each agent executes these actions
using some of the build-in functions, such as trade, production and
consumption of ABCE. The agents can use the full set of commands of the
Python general purpose language.

The audience of ABCE are economists that want to model agent-based
models of trade and production. It is especially geared towards
simulations that are similar to standard economic models
like general or partial equilibrium models [#noeq]_. What is more ABCE is
especially designed to make writing the simulation and the execution
fast. Therefore models can be developed in an interlinked process of
running and rewriting the simulation.

ABCE uses Python - a language that is especially beginner friendly, but also
easy to learn for people who already know object oriented programming
languages such as Java, C++ or even MATLAB.
Python allows simple, but fully functional, programming for economists.
What is more Python is readable even for non Python programmers.

.. [#scheduler] the Simulation class
.. [#noeq] with out the equilibrium of course

Design
------

ABCE's first design goal is that, code can be rapidly written,
to enable a modeler to quickly write down
code and quickly explore different alternatives of a model.

Execution speed is a secondary concern to the goal of rapid development.
Execution speed is achieved by making use of multiple-cores/processors.

Secondly, the modeler can concentrate on programming the behavior of the agents and
the specification of goods, production and consumption function.
The functions for economic simulations such as production, consumption,
trade, communication are provided and automatically performed by the platform.

Python has also been chosen as a programming language, because of
it's rich environment of standard libraries. Python for example
comes with a stock representation of agents in a spacial world,
which allow the modeler to model a spatial model although ABCE
was not designed for spatial models.

Python is a language that lends itself to writing of code fast, because it
has low overhead. In Python variables do not have to be declared, garbage
does not have to be collected and classes have no boiler-plate code.

Python, is slower than Java or C, but its reputation for slow speed is usually
exaggerated. Various packages for numerical calculations and optimization such as numpy and scipy offer
the C like speed to numerical problems. Contrary to the common belief
Python is not an interpreted language. Python is compiled to bytecode and
than executed. What is more Python in combination with ZeroMQ allows us
to parallelize the code and gain significant speed advantage over
single-threaded code, that does not make use of the speed advantage of
multi-core or multi-processor computers.

ABCE 0.3.1 supports Python 2.7, Python 3 support is planned for
the 0.5 release.

.. [#interpreter] Python is often falsely believe to be an interpreted language

One of the mayor impediments of speed is that the GIL - global interpreter lock -
of Python forces us to use the processing module instead of the threading module.
Using multi-threading would allow the usage of ZeroMQ's  'inproc' socket instead of the
slower 'ipc' or 'tpc' sockets. Once a GIL free version compatible with ZeroMQ is
available this speed break can readily be removed as the processing and the threading
module have the same API.

In the current 3.0.1 version simulations are not entirely deterministic,
the order of messages depends on which agent is called first. The call
order of the agents by the virtual parallelization is not necessarily
consistent. In other words, if your system has less cores than agents,
not all agents do actually run in parallel. The parallelization is achieved
by randomizing the message order. This leads to some agents sending the
messages (or goods) faster than others, which determines the order of
the messages before the randomization. The randomization in turn is not
deterministic. In the 4.0.0 the randomization will not depend on the
message order, but on the message id, which is a deterministic
combination of the agent's name, id and message’s sequence number.


Differences to other agent-based modeling platforms
---------------------------------------------------

We identified several survey articles as well as
a quite complete overview of agent-based modeling software
on Wikipedia. :raw-tex:`\cite{Serenko2002}`, :raw-tex:`\cite{Allan2010}`
:raw-tex:`\cite{Societies2009}`, :raw-tex:`\cite{Tobias2004}`, :raw-tex:`\cite{Railsback2006}`,
:raw-tex:`\cite{abmcomparisonWikipedia2013}`. The articles
'Tools of the Trade' by Madey and Nikolai :raw-tex:`\cite{Societies2009}`
and 'Survey of Agent Based Modelling and Simulation Tools' by Allan  :raw-tex:`\cite{Allan2010}`
attempt to give a complete overview
of agent-based modelling platforms/frameworks. The Madey and Nikolai paper
categorizes the abm-platforms according
to several categories. (Programming Language, Type of License,
Operating System and Domain). According to this article, there
is only one software platform which aims at the specific
domain of economics: JASA. But JASA is a modeling platform
that aims specifically at auctions.
Wikipedia :raw-tex:`\cite{abmcomparisonWikipedia2013}` lists JAMEL
as an economic platform, but JAMEL a is closed source and
an non-programming platform. The 'Survey of Agent Based Modelling and Simulation Tools'
by Allan :raw-tex:`\cite{Allan2010}` draws
our attention to LSD, which, as it states, is rather a system dynamic,
than an agent-based modeling platform. We conclude that
there is a market for a domain specific language for economics.

While the formerly mentioned modeling platforms aim to give a
complete overview, 'Evaluation of free Java - libraries for
social scientific agent based simulation' :raw-tex:`\cite{Tobias2004}`
by Tobias and Hoffman
chooses to concentrate on a smaller number of simulation packages.
Tobias and Hoffman discuss: RePast, Swarm, Quicksilver, and VSEit.
We will follow this approach and concentrate on a subset of
ABM models. First as economics is a subset of social science we
dismiss all platforms that are not explicitly targeted at
social science. The list of social science platforms according
to :raw-tex:`\cite{Societies2009}` Madey and Nikolai is:
AgentSheets, LSD, FAMOJA, MAML, MAS-SOC,  MIMOSE, NetLogo, Repast
SimBioSys, StarLogo, StarLogoT, StarLogo TNG, Sugarscape, VSEit
NetLogo and  Moduleco.
We dismiss some of these frameworks/platforms:

AgentSheets,
    because it is closed source and not 'programable'
LSD,
    because it is a system dynamics rather than an agent-based modeling environment
MAML,
    because it does not use a standard programming language, but his its own.
MAS-SOC,
    because we could not find it in the Internet and its documentation
    according to :raw-tex:`\cite{Allan2010}` is sparse.
MIMOSE,
    is an interesting language, but we will not analyze as it is based on a completely different
    programming paradigm, functional programming, as opposed to object-oriented
    programming.
SimBioSys,
    because it has according to Allan :raw-tex:`\cite{Allan2010}` and our research  a sparse documentation.
StarLogo, StarLogoT, StarLogo TNG,
    because they have been superseded by NetLogo
Moduleco,
    because it has  according to Allan :raw-tex:`\cite{Allan2010}` and our research a sparse documentation.
    Further, it appears not to be updated since roughly 2001

We will concentrate on the most widely used ABM frameworks/platforms: MASON, NetLogo, Repast.

General differences to other agent-based modeling platforms
===========================================================

First of all ABCE is domain specific, that enables it to provide
the basic functions such as production, consumption, trade and
communication as fully automated stock methods.
Because any kind of agent interaction (communication and exchange of
goods) is handled automatically ABCE, it can run the agents (virtually)
parallel and run simulations on multi-core/processor systems without
any intervention by the modeler.

The second biggest difference between ABCE and other platforms
is that ABCE introduces the physical good as an ontological object in
the simulation. Goods can be exchanged and transformed. ABCE handles
these processes automatically, so that for the model a physical good
behaves like a physical good and not like a message. That means that
if a good is transfered between two agents the first agent does not
have this good anymore, and the second agent has it now. Once, for
example, two agents decide to trade
a good ABCE makes sure that the transaction is cleared between
the two agents.

Thirdly, ABCE is just a scheduler that schedules the actions of
the agents and a python base class that enables the agent to
produce, consume, trade and communicate. A model written
in ABCE, therefore is standard Python code and the modeler can make
use of the complete Python language and the Python language environment.
This is a particular useful feature because Python comes with about 30.000 [#30000]_
publicly available packages, that could be used in ABCE. Particularly
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
and SugerScape and, in a
more limited sense, Repast are designed with spacial representation in mind.
For ABCE a spacial representation was explicitly not a design goal.
However, since agents in ABCE are ordinary Python objects, they can use
python modules such as python-turtle and therefore gain a spacial
representation much like NetLogo. This does by no means mean that
ABCE could not be a good choice for a problem where the spacial
position plays a role. If for example the model has different
transport costs or other properties according to the geographical
position of the agents, but the agent's do not move or the movement
does not have to be represented graphically, ABCE could still be a
reasonable choice.

.. [#30000] https://pypi.python.org/

Physical Goods
==============

Physical goods are at the heart of almost every economic model.
The core feature and main difference to other ABM platforms is the
implementation of physical goods. In contrast
to information or messages, sharing a good means having less of it. In other
words if agent A gives a good to agent B then agent A does not have this good
anymore. On of the major strength of ABCE is that this is automatically handled.

In ABCE goods can be created, destroyed, traded, given or changed through
production and consumption. All these functions are implemented in ABCE and
can be inherited by an agent as a method. These functions are automatically handled by
ABCE upon decision from the modeler.

Every agent in ABCE must inherit from the abce.Agent class. This gives the
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

Difference to MASON
===================

Masons is a single-threaded discrete event platform that is intended
for simulations of social, biological and economical systems.
:raw-tex:`\cite{Luke}`. Mason is a platform that was explicitly designed with the goal of
running it on large platforms. MASON distributes a large number
of single threaded simulations over deferent computers or processors.
ABCE on the other hand is multi-threaded it
allows to run agents in parallel. A single run of a simulation
in MASON is therefore not faster on a computing cluster than
on a potent single-processor computer. ABCE on the other hand
uses the full capacity of multi-core/processor systems for
a single simulation run. The fast
execution of a model in ABCE allow a different software
development process, modelers can 'try' their models while they
are developing and adjust the code until it works as desired.
The different nature of both
platforms make it necessary to implement a different event
scheduling system.

Mason is a discrete event platform. Events can be scheduled by the
agents. ABCE on the other hand is scheduled -
it has global list of sub-rounds that establish the sequence
of actions in every round. Each of these sub-rounds lets a
number of agents execute the same actions in parallel.

This, however does not mean that the order of actions is
fixed. It is possible that one sub-round leads to different
actions according to the internal logic of the agent. An
implementation of a discrete event scheduler like in MASON
is on the TODO list for ABCE.

MASON, like Repast Java is based on Java, while ABCE is
based on Python, the advantages have been discussed before.

MASON comes with a visualization layer. ABCE, does not have
this feature for several reasons. First spacial models are
not an explicit design goal of ABCE. Second for models
that have a spacial representation the Python's standard
turtle library can be used and ad Netlogo like functionality.
Thirdly ABCE has the ability of detailed statistical output,
which can be readily visualized with standard software,
such as R and Excel.

One form of spacial representation in MASON are networks.
Networks in ABCE must be created by hand: in ABCE directed links
of an agent are simply a Python-list with the id-numbers of the
agents that are connected to it.


Difference to NetLogo
=====================

Netlogo is a multi-agent programming language, which is part of
the Lisp language family. Netlogo is interpreted.
:raw-tex:`\cite{Tisue2004}` Python on the
other hand is a compiled [#compiled]_ general programming language.
Consequently it is faster than NetLogo.

NetLogo has the unique feature to integrate the interface with
with the programming language. ABCE goes a different direction
rather than integrating the interface it forgoes the interface
completely and everything is written in Python (even the
configuration files), parameters are specified in excel-sheets (.csv).

Netlogo's most prominent feature are the turtle agents. To
have turtle agents in ABCE, Python's turtle library has to be
used. The graphical representation of models is therefore not
part of ABCE, but of Python itself, but needs to be included by
the modeler.

One difference between Netlogo and ABCE is that it has the
concept of the observer agent, while in ABCE the simulation
is controlled by the simulation process.

Difference Repast
=================

Repast is a modeling environment for social science. It was
originally conceived as a Java recoding of SWARM.
:raw-tex:`\cite{Collier}` :raw-tex:`\cite{NORTH2005}` Repast
comes in several flavors: Java, .Net, and a Python like
programming language. Repast has been superseded by
Repast Symphony which maintains all functionality, but
is limited to Java. Symphony has a point and click
interface for simple models. :raw-tex:\cite{NORTH2005a}


Repast does allow static and dynamic scheduling.
:raw-tex:`\cite{Collier}`. ABCE,
does not (yet) allow for dynamic scheduling. In ABCE, the
order of actions - or in ABCE language order of sub-rounds -
is fixed and is repeated for every round. This however is not
as restrictive as it sounds, because in any sub-round an
agent could freely decide what he does.

The advantage of the somehow more limited implementation of
ABCE is ease of use. While in Repast it is necessary to
subclass the scheduler in ABCE it is sufficient to specify
the schedule and pass it the Simulation class.

Repast is vast, it contains 210 classes in 9 packages
:raw-tex`\cite{Collier}`. ABCE, thanks to its limited
scope and Python, has only 6 classes visible to the
modeler in a single package.




.. [#compiled]  Python contrary to the common believe is compiled to bytecode similar to Java's compilation to bytecode.



