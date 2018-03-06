How to share public information?
--------------------------------

Agents can return information via a return statement at the end of a method.
The returned variables are returned to start.py as a list of the values. It
is often useful to include the agents name e.G. :code:`return (self.name, info)`

The returned information can than be passed as arguments for another method::

    for r in range(100):
        simulation.advance_round(r)
        agents.do_something()
        info = agents.return_info()
        agents.receive_public_information(info=info)

Currently only named function parameters are supported.


How to share a global state?
----------------------------

A shared global state, breaks multiprocessing, so if you want to run the simulation
on multiple cores see 'How to share public information'. In single processing mode, you can give each agent a dictionary as a parameter. All information in this dictionary is shared.

How to access other agent's information?
----------------------------------------

Once again this breaks multiprocessing. But you can return an agent's self and give it as a parameter to other agents.

How to make abcEconomics fast?
------------------------------

There is several ways:

#. Use pypy3 instead of CPython, it can be downloaded here: https://pypy.org/download.html. With pypy3 you can run the same code as with CPython, but about 30 times faster.

#. If you use scipy pypy3 might not work. Use numba instead. http://numba.pydata.org

#. Run the simulation with a different number of processes. With very simple agents and many messages one is optimal, with compute intensive agents number of physical processors minus one is usually most efficient. But experimenting even with more processes than physical processors might be worth it.

#. Use kernprof to find which agent's method is slowest. https://github.com/rkern/line_profiler

How to load agent-parameters from a csv / excel / sql file?
-----------------------------------------------------------

The list of parameters can be passed as agent_parameters and is passed to init, as
keyword arguments::

    with open('emirati.csv', 'r') as f:
        emirati_file = csv.DictReader(f)
        emiratis_data = list(emirati_file)


    emiratis = sim.build_agents(Emirati, 'emirati', agent_parameters=emiratis_data)

Note that list(file) is necessary.



