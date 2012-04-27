from agentengine import *


class Agent(AgentEngine,):
    def __init__(self, arguments):
        AgentEngine.__init__(self, *arguments)
        if self.name[0] == 'a':
            self.create('red_ball', self.idn)
        else:
            self.create('blue_ball', self.idn)

        self.create('money', 10)
        self.red_to_blue = create_production_function('blue_ball=red_ball')
        if self.idn == 0:
            self.painter = True
        else:
            self.painter = False
        print(self.name)

    def give(self):
        """ gives the next agent all balls, if he has one """
        #print("give")
        reciever = self.next_agent()
        if self.count('red_ball') > 0:
            self.sell(reciever, "red_ball", self.count('red_ball'), 1)
        if self.count('blue_ball') > 0:
            self.sell(reciever, "blue_ball", self.count('blue_ball'), 1)

    def get(self):
        """ accepts all balls """
        #print("get")
        offers = self.open_offers_all()

        if offers:
            offer = offers[0]
            try:
                self.accept(offer)
            except NotEnoughGoods as inst:
                print(inst)
        else:
            print(self.name, 'no offers')

    def report(self):
        #print("report")
        print(self.name, ':', "have", self.count('blue_ball'), "blue balls", self.count('red_ball'), "red balls", self.count('money') , "$")

    def next_agent(self):
        return agent_name(self.name[0:5], (1 + self.idn) % 3)
