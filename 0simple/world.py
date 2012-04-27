from worldengine import *

class World(WorldEngine):
    """ Calls the ActionGroups in the order specified in self.actionList.
    """
    def __init__(self, parameter_file):
        WorldEngine.__init__(self, parameter_file)
        self.action_list = ["give", "get", "report"]

    def give(self):
        print('give')
        self.ask_each_agent_in("agent", "give")
        self.ask_each_agent_in("bgent", "give")

    def get(self):
        print('get')
        self.ask_each_agent_in("agent", "get")
        self.ask_each_agent_in("bgent", "get")

    def report(self):
        print('report')
        self.ask_agent("agent_0", "report")
        time.sleep(0.1)
        self.ask_agent("agent_1", "report")
        time.sleep(0.1)
        self.ask_agent("agent_2", "report")
        time.sleep(0.1)
        self.ask_agent("bgent_0", "report")
        time.sleep(0.1)
        self.ask_agent("bgent_1", "report")
        time.sleep(0.1)
        self.ask_agent("bgent_2", "report")