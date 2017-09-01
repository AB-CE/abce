Graphical User Interface
========================

.. automodule:: abce.show

.. autofunction:: abce.gui.gui

.. automethod:: abce.Simulation.graphs

It is possible to add text frames between the simulation results. In order to
add a text frame to the simulation output, simply add a text file :code:`.txt`
or :code:`.html` in either your source code directory or if generated during
the simulation in the :code:`simulation.path` directory (where the
:code:`.csv` are). The first line of the text file is the title the rest the
text. The text can be formatted as html, the first line is separate from the
rest.
In the simulation results all frames are displayed in alphabetical order, the
title in the first line of the text-file determines the position where the text frame is
displayed. In order to display a text before all graphs, you have to put
leading space (' ') in front of the title.
