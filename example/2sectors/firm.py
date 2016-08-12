from __future__ import division, print_function
import abce


class Firm(abce.Agent, abce.Firm):
    def init(self, simulation_parameters, agent_parameters):
        """ there are now 2 sectors:
        - upstream produces an intermediary good
        - downstream uses labor and the intermediary good to produce the final good

        there is an initial endowment to avoid bootstrapping problems
        """
        print(agent_parameters)
        self.price = {}
        if self.id % 2 == 0:
            assert self.id == 0
            self.create('money', 2)
            self.inputs = {"labor": 1}
            self.output = "intermediate_good"
            self.outquatity = 1
            self.price['intermediate_good'] = 1
        elif self.id % 2 == 1:
            assert self.id == 1
            self.create('money', 1)
            self.create('intermediate_good', 1)
            self.inputs = {"labor": 1, "intermediate_good": 1}
            self.output = "consumption_good"
            self.outquatity = 2
            self.price['consumption_good'] = 1
        self.set_cobb_douglas(self.output, self.outquatity, self.inputs)

    def buy_inputs(self):
        oo = self.get_offers("labor")
        for offer in oo:
            self.accept(offer)
        oo = self.get_offers('intermediate_good')
        for offer in oo:
            self.accept(offer)

    def production(self):
        self.produce(self.inputs)

    def sell_intermediary_goods(self):
        if self.output == 'intermediate_good':
            self.sell('firm', 1, "intermediate_good", 1, 1)
        elif self.output == 'consumption_good':
            for i in range(2):
                self.sell('household', i, 'consumption_good', 1, 1)
