============
Introduction
============

ABCE is a Python Agent-Based Complete Economy Platform, written by Davoud Taghawi-Nejad.
With ABCE, you can write economic, agent-based simulations in python. ABCE handles,
trading production an consumption automatically. The agents, written by the modeler
do only have to make the decisions and instruct the platform to trade, produce and
consume. ABCE makes sure the economy is closed, that means no goods appear, disappear
or are otherwise unaccounted for. It is therefore particularly useful for macro models.
ABCE's model output are compatible with R, Excel and sqlite.

.. image:: https://zenodo.org/badge/4157636.svg
   :target: https://zenodo.org/badge/latestdoi/4157636

.. image:: https://travis-ci.org/AB-CE/abce.svg?branch=master
   :alt: ABCE build status on Travis CI
   :target: https://travis-ci.org/AB-CE/abce

.. image:: https://img.shields.io/appveyor/ci/AB-CE/abce.svg
   :alt: ABCE build status on Appveyor CI
   :target: https://ci.appveyor.com/project/AB-CE/abce

.. image:: https://img.shields.io/pypi/v/abce.svg
   :alt:  Pypi version
   :target: https://pypi.python.org/pypi/abce

.. image:: https://readthedocs.org/projects/abce/badge/?version=master
   :alt:  readthedocs
   :target: https://abce.readthedocs.io


**The full documentation:** https://abce.readthedocs.io

--------
Features
--------

- Built-in standard actions for economic agents: `get_offers`, `sell`/`buy`/`retract`,
  `accept`/`reject`/`take` -- optimized in Cython
- In the simulation, goods are ontological object instead of epistemological
  information that lives in a ledger
- Stock-flow consistent model
- Discrete-time scheduler
- Parallel execution of actions within a subround via `multiprocessing`
- Browser-based GUI via `@gui` decorator


------------
Installation
------------

You can quickly install ABCE from a terminal,

```
$ pip install git+https://github.com/ABC-E/abce
```

or from this repo

```
$ pip install .
```
