import abce


class MyAgent(abce.Agent):
    def init(self, sp, ap):
        print('init', ap)
        self.mine = ap
        self.diff = False

    def call_me_maybe(self):
        print(self.name, self.mine)


class DifferentAgent(abce.Agent):
    def init(self, sp, ap):
        print('init', ap)
        self.mine = ap
        self.diff = True

    def call_me_maybe(self):
        print('I am different', self.name, self.mine)


sim = abce.Simulation()

myagent = sim.build_agents(MyAgent, 'myagent',
                           agent_parameters=[{'agent_parameters': 0},
                                             {'agent_parameters': 1},
                                             {'agent_parameters': 2},
                                             {'agent_parameters': 3},
                                             {'agent_parameters': 4},
                                             {'agent_parameters': 5},
                                             {'agent_parameters': 6}])

differentagent = sim.build_agents(DifferentAgent, 'differentagent',
                                  agent_parameters=[{'agent_parameters': 0},
                                                    {'agent_parameters': 1},
                                                    {'agent_parameters': 2},
                                                    {'agent_parameters': 3},
                                                    {'agent_parameters': 4},
                                                    {'agent_parameters': 5},
                                                    {'agent_parameters': 6}])

print('len', len(myagent))

sim.advance_round(0)
myagent.call_me_maybe()
print('simple')

for r in range(1, 14):
    sim.advance_round(r)
    myagent[r % 7].call_me_maybe()
    print('--')

print('two individuals')
for r in range(14, 28):
    (myagent[r % 7] + myagent[3]).call_me_maybe()
    print('--')

print('one class')
for r in range(28, 42):
    sim.advance_round(r)
    myagent[r % 7, 3].call_me_maybe()
    print('--')

print('whole class plus individual')
for r in range(42, 56):
    sim.advance_round(r)
    (myagent + myagent[r % 7]).call_me_maybe()
    print('--')

print('two classes')
for r in range(56, 70):
    sim.advance_round(r)
    (myagent + differentagent).call_me_maybe()
    print('--')

sim.finalize()
