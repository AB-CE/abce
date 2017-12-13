import abce


class Agent(abce.Agent):
    def actionA(self):
        print(self.name, 'actionA')

    def actionB(self):
        print(self.name, 'actionB')


def main(processes, rounds):
    sim = abce.Simulation(processes=processes)

    aagents = sim.build_agents(Agent, 'aagent', number=5)
    bagents = sim.build_agents(Agent, 'bagent', number=5)

    actionA = aagents.actionA
    actionB = bagents.actionB

    for r in range(rounds):
        sim.advance_round(r)
        (aagents.actionA + aagents.actionB)()
        (aagents.actionA + bagents.actionB)()
        (aagents.actionB + bagents.actionB)()
        aagents.actionA()
        bagents.actionB()
        (actionA + actionB)()

    sim.finalize()


if __name__ == '__main__':
    main(1, 1)
    main(4, 1)
