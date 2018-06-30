Create Plugins
==============

abcEconomics has three plugin so far: abcFinance, abcLogistics, abcCython. If
you want to author your own plugin - its dead simple. All you
have to do is write a class that inherits from Agent in agent.py.
This class can overwrite::

    def __init__(self, id, group, trade_logging, database, random_seed, num_managers,
                 agent_parameters, simulation_parameters,
                 check_unchecked_msgs, start_round=None):
    def _begin_subround(self):
    def _end_subround(self):
    def _advance_round(self, time):

For example like this::

    class UselessAgent(abcEconomics.Agent):
        def __init__(self, id, group, trade_logging, database, random_seed, num_managers,
                     agent_parameters, simulation_parameters,
                     check_unchecked_msgs, start_round=None):
            super().__init__(id, group, trade_logging,
                             database, random_seed, num_managers, agent_parameters,
                             simulation_parameters, check_unchecked_msgs,
                             start_round):
            print("Here i begin")

        def _begin_subround(self):
            super()._begin_subround()
            print('subround begins')

        def _end_subround(self):
            super()._end_subround()
            print('subround finishes')

        def _advance_round(self, time):
            super()._advance_round(time)
            print('Super I made it to the next round')

        def ability(self):
            print("its %r o'clock" % self.time)
            print("the simulation called my ability")


**Do not overwrite the init(parameters, simulation_parameters)** method


Database Plugins
================

In order to write custom logging functions, create a class with your custom logging::

    class CustomLogging:
        def __init__(self, dbname, tablename, arg3):
            self.db = dataset.connect('sqlite:///factbook.db')
            self.table = self.db[tablename]


        def write_everything(self, name, data):
            self.table.insert(dict(name=name, data=data))

        def close(self):
             self.db.commit()

The close method is called when the simulation in ended with simulation.finalize().


The CustomLogging class must be given to the simulation, in will be initialized with the dbpluginargs argument list::

    sim = Simulation(name='mysim', dbplugin=CustomLogging, dbpluginargs=['somedb.db', 'sometable', 'arg3')

The agents can execute your custom logging function like this::

    self.custom_log('write_everything', name='joe', data=5)


