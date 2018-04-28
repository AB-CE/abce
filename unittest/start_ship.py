import abce
from abce import tradewithshipping


class Shipper(tradewithshipping.TradeWithShipping, abce.Agent):
    def init(self):
        for i in range(10):
            self.create('g%i' % i, 10)

    def ship_(self):
        self.ship(('receiver', 0),
                  good='g%i' % self.time,
                  quantity=self.time,
                  arrival=self.time + 3)


class Receiver(tradewithshipping.TradeWithShipping, abce.Agent):
    def init(self):
        pass

    def receive(self):
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


def main():
    sim = abce.Simulation()
    receiver = sim.build_agents(Receiver, 'receiver', number=1)
    shipper = sim.build_agents(Shipper, 'shipper', number=1)

    for r in range(10):
        sim.advance_round(r)
        shipper.ship_()
        receiver.receive()
    sim.finalize()


if __name__ == '__main__':
    main()
