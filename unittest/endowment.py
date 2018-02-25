import abce


class Endowment(abce.Agent, abce.Household):
    def init(self, rounds, creation):
        self.last_round = rounds - 1
        self.creation = creation
        self.create('labor_endowment', 1)
        self.create('cow', 1)
        self.utility_function = self.create_cobb_douglas_utility_function({'milk': 2})

    def Iconsume(self):
        assert self['labor'] == 5, self['labor']
        assert self['milk'] == 10 + (self.round - self.creation) * (10 - 3), (10 + (
            self.round - self.creation) * (10 - 3), self['milk'], self.creation)
        milk = self['milk']
        utility = self.consume(self.utility_function, {'milk': 3})
        assert utility == 9, utility
        assert milk - 3 == self['milk'], self['milk']

    def all_tests_completed(self):
        if self.round == self.last_round and self.id == 0:
            print('Test declare_round_endowment:\t\t\tOK')
            print('Test s.declare_perishable:\t\t\tOK')
            # utility testnot exaustive!
