import abce


class Endowment(abce.Agent, abce.Household):
    def init(self, simulation_parameters, agent_parameters):
        self.last_round = simulation_parameters['rounds'] - 1
        self.creation = simulation_parameters['creation']
        self.create('labor_endowment', 1)
        self.create('cow', 1)
        self.set_cobb_douglas_utility_function({'milk': 2})

    def Iconsume(self):
        assert self['labor'] == 5, self['labor']
        assert self['milk'] == 10 + (self.round - self.creation) * (10 - 3), (10 + (
            self.round - self.creation) * (10 - 3), self['milk'], self.creation)
        milk = self['milk']
        utility = self.consume({'milk': 3})
        assert utility == 9, utility
        assert milk - 3 == self['milk'], self['milk']

    def all_tests_completed(self):
        if self.round == self.last_round and self.id == 0:
            print('Test declare_round_endowment:\t\t\tOK')
            print('Test s.declare_perishable:\t\t\tOK')
            # utility testnot exaustive!
