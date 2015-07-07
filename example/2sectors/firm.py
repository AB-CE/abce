from __future__ import division
import abce


class Firm(abce.Agent, abce.Firm):
    def __init__(self, simulation_parameters, agent_parameters, _pass_to_engine):
        """ there are now 2 sectors:
        - upstream produces an intermediary good
        - downstream uses labor and the intermediary good to produce the final good

        there is an initial endowment to avoid bootstrapping problems
        """
        abce.Agent.__init__(self, **_pass_to_engine)
        self.price = {}
        self.sector = agent_parameters['sector']
        if self.sector == 'intermediate_good':
            assert self.idn == 0
            self.create('money', 2)
            self.inputs = {"labor": 1}
            self.output = "intermediate_good"
            self.outquatity = 1
            self.price['intermediate_good'] = 1
        elif self.sector == 'consumption_good':
            assert self.idn == 1
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
        if self.sector == 'intermediate_good':
            self.sell('firm', 1, "intermediate_good", 1, 1)
        elif self.sector == 'consumption_good':
            for i in range(2):
                self.sell('household', i, 'consumption_good', 1, 1)
