import abcEconomics
import dataset


class CustomLogging:
    def __init__(self, dbprotocolname, tablename):
        self.db = dataset.connect(dbprotocolname)
        self.table = self.db[tablename]

    def write_everything(self, **kveverything):
        self.table.insert(kveverything)

    def close(self):
        self.db.commit()


class MyAgent(abcEconomics.Agent):
    def write(self):
        self.custom_log('write_everything', name='joe', m=5)


def main(processes, rounds):
    sim = abcEconomics.Simulation(name='mysim', processes=processes, dbplugin=CustomLogging, dbpluginargs=['sqlite:///:memory:', 'sometable'])

    myagents = sim.build_agents(MyAgent, 'myagent', number=5)

    for i in range(rounds):
        sim.advance_round(i)
        myagents.write()

    sim.finalize()


if __name__ == '__main__':
    main(1, 5)
    main(4, 5)
