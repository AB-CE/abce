
With this basic understanding from the walk through we can now start writing your own model.

This is a step by step guide to create an agent-based model with ABCE.
We will create a simple economy of one household and one firm. The household and the
firm trade with each other at fixed prices and quantities. You can than make the
model more realistic by implementing price and decision rules for yourself.
In the following two text boxes, the two concepts that make ABCE special are
explained: The explicit modeling of trade-able goods and the optional concept
of a physically closed economy.


To create a model you have to follow three steps:

    1. Specify endowments that replenish every round and goods / services that perish
    2. Specify the order of actions
    3. Write the agents with their actions

There is of course a little bit of administrative work you have to do:

    1. import agents in the model
    2. specify parameters
