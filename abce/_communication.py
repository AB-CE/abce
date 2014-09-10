# Copyright 2012 Davoud Taghawi-Nejad
#
# Module Author: Davoud Taghawi-Nejad
#
# ABCE is open-source software. If you are using ABCE for your research you are
# requested the quote the use of this software.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License and quotation of the
# author. You may obtain a copy of the License at
#       http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.
""" internal process handles communication
"""
import abce.jzmq as zmq
try:
    from multiprocessing import Process
except ImportError:
    from threading import Thread as Process


class _Communication(Process): #pylint: disable=R0903
    def __init__(self, _addresses_bind, _addresses_connect, context): #pylint: disable=W0231
        Process.__init__(self)
        self._addresses_bind = _addresses_bind
        self._addresses_connect = _addresses_connect
        self.context = context

    def run(self): #pylint: disable=R0915,R0912
        self.in_soc = self.context.socket(zmq.PULL)
        self.in_soc.bind(self._addresses_bind['frontend'])

        self.out = self.context.socket(zmq.PUSH)
        self.out.bind(self._addresses_bind['backend'])

        self.shout = self.context.socket(zmq.PUB)
        self.shout.bind(self._addresses_bind['group_backend'])

        self.ready = self.context.socket(zmq.PUSH)
        self.ready.connect(self._addresses_connect['ready'])
        agents_finished, total_number = 0, 0
        total_number_known = False
        self.ready.send('working')
        all_agents = []
        while True:
            try:
                msg = self.in_soc.recv_multipart()
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
                    self.shout.send_multipart(msg[2:])
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
                        self.ready.send('.')
                        if send_end_of_communication_sign:
                            for agent in all_agents:
                                self.out.send_multipart([agent, '.'])
                            self.shout.send('all.')
            else:
                self.out.send_multipart(msg)
        self.context.destroy()
