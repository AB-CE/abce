class repeat:
    """ Repeats the contained list of actions several times

    Args:

     action_list:
        action_list that is repeated

     repetitions:
        the number of times that an actionlist is repeated or the name of
        the corresponding parameter in simulation_parameters.csv

    Example with number of repetitions in simulation_parameters.csv::

        action_list = [
            repeat([
                    ('firm', 'sell'),
                    ('household', 'buy')
                ],
                repetitions=parameter['number_of_trade_repetitions']
            ),
            ('household_03', 'dance')
            'panel_data_end_of_round_before consumption',
            ('household', 'consume'),
            ]
        s.add_action_list(action_list)

    """
    def __init__(self, action_list, repetitions):
        self.action_list = action_list
        self.repetitions = repetitions


class repeat_while:
    """ NOT IMPLEMENTED Repeats the contained list of actions until all agents_risponed
    done. Optional a maximum can be set.

    Args::

     action_list: action_list that is repeated
     repetitions: the number of times that an actionlist is repeated or the name of
     the corresponding parameter in simulation_parameters.csv

    """
    #TODO implement into _process_action_list
    def __init__(self, action_list, repetitions=None):
        SystemExit('repeat_while not implement yet')
        self.action_list = action_list
        if repetitions:
            try:
                    self.repetitions = int(repetitions)
            except ValueError:
                try:
                    self.repetitions = self.simulation_parameters[repetitions]
                except KeyError:
                    SystemExit('add_action_list/repeat ' + repetitions + ' is not a number or'
                    'a column name in simulation_parameters.csv or the parameterfile'
                    'you choose')
        else:
            self.repetitions = None
        raise SystemExit('repeat_while not implemented')
        #TODO implement repeat_while
