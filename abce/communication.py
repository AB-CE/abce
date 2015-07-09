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

    def set_agents(self, agents_backend):
        self.agents_backend = agents_backend


    def run(self):
        agents_finished, total_number = 0, 0
        total_number_known = False
        self.ready.put('working')
        try:
            while True:
                msg = self.in_soc.get()
                if msg[0] == '!':
                    if msg[1] == '.':
                        agents_finished += 1
                    elif msg[1] == '+':
                        total_number += int(msg[2])
                        continue
                    elif msg[1] == '!':
                        if msg[2] == 'end_simulation':
                            break
                    if agents_finished == total_number:
                        agents_finished, total_number = 0, 0
                        total_number_known = False
                        self.ready.put('.')
                else:
                    if msg[1] == 'all':
                        for agent in self.agents_backend['all'][msg[0]]:
                            agent.put(msg[2:])
                    else:
                        self.agents_backend[msg[0]][msg[1]].put(msg[2])
        except KeyboardInterrupt:
                print('KeyboardInterrupt: _Communication: Waiting for messages')
