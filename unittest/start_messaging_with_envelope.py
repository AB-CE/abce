import abcEconomics


class MessageA(abcEconomics.Agent):
    def init(self):
        # your agent initialization goes here, not in __init__
        pass

    def sendmsg(self):
        self.send_envelope(('messageb', self.id), 'msg', 'hello there')

    def recvmsg(self):
        msg = self.get_messages('msg')[0].content
        assert msg == 'hello there'


class MessageB(abcEconomics.Agent):
    def init(self):
        # your agent initialization goes here, not in __init__
        pass

    def sendmsg(self):
        self.send_envelope(('messagea', self.id), 'msg', 'hello there')

    def recvmsg(self):
        assert self.get_messages('msg')[0].content == 'hello there'


def main(processes, rounds):
    s = abcEconomics.Simulation(processes=processes, name='unittest')

    print('build MessageA')
    messagea = s.build_agents(MessageA, 'messagea', 20)
    print('build MessageB')
    messageb = s.build_agents(MessageB, 'messageb', 20)

    for r in range(rounds):
        s.time = r
        (messagea + messageb).sendmsg()
        (messageb + messagea).recvmsg()

    print("Send_envelope and receive test:\t OK")
    s.finalize()


if __name__ == '__main__':
    main(processes=1, rounds=5)
    print('Iteration with 1 core finished')
    main(processes=2, rounds=5)
    print('Iteration with multiple processes finished')
