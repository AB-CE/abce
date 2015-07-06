import zmq
import multiprocessing as mp


class Communication(mp.Process):
    def __init__(self):
        mp.Process.__init__(self)
        self.in_soc = mp.Queue()
        self.out = mp.Queue()
        self.ready = mp.Queue()

    def get_queue(self):
        """ returns frontend, backend, ready """
        return self.in_soc, self.out, self.ready

    def run(self):
        agents_finished, total_number = 0, 0
        total_number_known = False
        self.ready.put('working')
        all_agents = []
        while True:
            try:
                msg = self.in_soc.get()
                print("communication - msg", msg)
            except KeyboardInterrupt:
                print('KeyboardInterrupt: _Communication: Waiting for messages')
                if total_number_known:
                    print("total number known")
                    print("%i of %i ended communication" % (agents_finished, total_number))
                else:
                    print("total number not known")
                break
            if msg[0] == '!':
                if msg[1] == '.':
                    agents_finished += 1
                if msg[1] == 's':
                    self.shout.put(msg[2:])
                    continue
                elif msg[1] == '+':
                    total_number += int(msg[2])
                    continue
                elif msg[1] == ')':
                    total_number_known = True
                    send_end_of_communication_sign = False
                elif msg[1] == '}':
                    total_number_known = True
                    send_end_of_communication_sign = True
                elif msg[1] == '!':
                    if msg[2] == 'register_agent':
                        all_agents.append(msg[3])
                        agents_finished += 1
                    elif msg[2] == 'end_simulation':
                        break
                if total_number_known:
                    if agents_finished == total_number:
                        agents_finished, total_number = 0, 0
                        total_number_known = False
                        self.ready.put('.')
                        if send_end_of_communication_sign:
                            for agent in all_agents:
                                self.out.put([agent, '.'])
            else:
                self.out.put(msg)
