import abce
from abce import tradewithshipping


class Shipper(tradewithshipping.TradeWithShipping, abce.Agent):
    def ship_(self):
        assert self['money'] == 0

        self.create('money', self.time * self.time)
        self.buy(('receiver', 0),
                 good='g%i' % self.time,
                 quantity=self.time,
                 price=self.time,
                 arrival=self.time + 3)

        assert self['g%i' % self.time] == 0
        assert self['g%i' % (self.time - 1)] == 0
        assert self['g%i' % (self.time - 2)] == 0
        assert self['g%i' % (self.time - 3)] == 0
        self.receive_shipments()
        print(self.possessions())
        if self.time > 3:
            assert self['g%i' % self.time] == 0
            assert self['g%i' % (self.time - 1)] == 0
            assert self['g%i' % (self.time - 2)] == 0
            assert self['g%i' % (self.time - 3)] == self.time - 3, (
                'g%i' % (self.time - 3), self['g%i' % (self.time - 3)])


class Receiver(tradewithshipping.TradeWithShipping, abce.Agent):
    def init(self):
        pass

    def receive(self):
        offers = self.get_bids('g%i' % self.time)
        assert len(offers) == 1
        assert not self.get_offers_all()
        offer = offers[0]
        assert offer.quantity == self.time
        self.create(offer.good, offer.quantity)
        self.accept(offer)
        assert self[offer.good] == 0


def main(processes):
    sim = abce.Simulation(processes=processes)
    receiver = sim.build_agents(Receiver, 'receiver', number=1)
    shipper = sim.build_agents(Shipper, 'shipper', number=1)

    for r in range(10):
        sim.advance_round(r)
        shipper.ship_()
        receiver.receive()
    sim.finalize()


if __name__ == '__main__':
    main(processes=1)
    main(processes=4)
