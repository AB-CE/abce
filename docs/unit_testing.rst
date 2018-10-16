unit testing
------------

One of the major problem of doing science with simulations is that
results found could be a mere result of a mistake in the software
implementation. This problem is even stronger when emergent phenomena
are expected. The first hedge against this problem is of course
carefully checking the code. abcEconomics and Pythons brevity  and readability
are certainly helping this. However structured testing procedures
create more robust software.

Currently all trade and exchange related as well as endowment, production
utility and data logging facilities are unit tested. It is planned to extend
unit testing to quotes, so that by version 1.0 all functions of the agents
will be fully unit tested.

The modeler can run the unit testing facilities on his own system and therefore
assert that on his own system the code runs correctly.

Unit testing is the testing of the testable part of a the software code.
:raw-tex:`\cite{Xie2007}`. As in abcEconomics the most crucial functions are
the exchange of goods or information, the smallest testable unit is often
a combination of two actions :raw-tex:`\cite{Aniche}`. For example making an offer and then by
a second agent accepting or rejecting it. The interaction and concurrent
nature of abcEconomics simulation make it unpractical to use the standard unit
testing procedures of Python.

:raw-tex:`\cite{Ellims2006}` argue that unit-testing is economical. In
the analysis of three projects they find that unit-testing finds errors
in the code and argue that its cost is often exaggerated. We can
therefore conclude that unit-testing is necessary and a cost efficient
way of ensuring the correctness of the results of the simulation. For
the modeler this is an additional incentive to use abcEconomics, if he
implemented the simulation as a stand alone program he would either have
to forgo the testing of the agent's functions or write his own unit-testing
facilities.
