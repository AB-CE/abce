import world
import zmq
import conventions


class Controller:
    def __init__(self):
        self.commands = world.context.socket(zmq.PUB)
        self.commands.bind("inproc://commands")
        self.ready = world.context.socket(zmq.PULL)
        self.ready.bind("inproc://ready")

    def wait_until_all_ready(self):
        for i in range(world.parameters.number_of_agents):
            self.ready.recv()

    def askEachAgentIn(self, com):
        """applying a method to a collection of instances
        collection, method, dict. of the parameters (may be empty)
        """
        self.commands.send_multipart(["all", com])
        self.wait_until_all_ready()

    def askAgent(self, agent, command):
        """applying a method to an instance of a class
        agent, method, dict. of the parameters (may be empty)
        """
        self.commands.send_multipart([idname(agent), command])
        self.ready.recv()

def idname(ID):
    return str(world.parameters.agent_name_format % ID)
