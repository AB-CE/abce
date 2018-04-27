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
""" This is the agent's facility to send and receive messages. Messages can
either be sent to an individual with :meth:`messaging.Messaging.message` or to a group with
:meth:`messaging.Messaging.message_to_group`. The receiving agent can either get all messages
with  :meth:`messaging.Messaging.get_messages_all` or messages with a specific topic with
:meth:`messaging.Messaging.get_messages`.
"""
from random import shuffle


class Message(object):
    __slots__ = ['sender', 'receiver', 'topic', 'content']

    def __init__(self, sender, receiver, topic, content):
        self.sender = sender
        self.receiver = receiver
        self.topic = topic
        self.content = content

    def __getitem__(self, item):
        return self.content[item]

    def __repr__(self):
        return "<{sender: %s; receiver: %s; topic: %s; content: %s}>" % (
            str(self.sender), str(self.receiver), self.topic, str(self.content))


class Messaging:
    def __init__(self, id, agent_parameters, simulation_parameters, group, trade_logging,
                 database, check_unchecked_msgs, expiring, perishable, resource_endowment, start_round=None):
        super(Messaging, self).__init__(id, agent_parameters, simulation_parameters, group, trade_logging, database,
                                        check_unchecked_msgs, expiring, perishable, resource_endowment, start_round)

    def send(self, receiver, topic, content):
        """ sends a message to agent. Agents receive it
        at the beginning of next round with :meth:`~abceagent.Messaging.get_messages` or
        :meth:`~abceagent.Messaging.get_messages_all`.

        Args::

            receiver:
                The name of the receiving agent a tuple (group, id).
                e.G. ('firm', 15)

            topic:
                string, with which this message can be received

            content:
                string, dictionary or class, that is send.

        Example::

            ... household_01 ...
            self.message('firm', 01, 'quote_sell', {'good':'BRD', 'quantity': 5})

            ... firm_01 - one subround later ...
            requests = self.get_messages('quote_sell')
            for req in requests:
                self.sell(req.sender, req.good, reg.quantity, self.price[req.good])

        Example2::

         self.message('firm', 01, 'm', "hello my message")

        """
        msg = Message(sender=self.name,
                      receiver=receiver,
                      topic=topic,
                      content=content)
        self._send(receiver[0], receiver[1], topic, msg)

    def get_messages(self, topic='m'):
        """ self.messages() returns all new messages send with :meth:`~abceagent.Messaging.message`
        (topic='m'). The order is randomized. self.messages(topic) returns all
        messages with a topic.

        A message is a string with the message. You can also retrieve the sender
        by `message.sender_group` and `message.sender_id` and view the topic with
        'message.topic'. (see example)

        If you are sending a float or an integer you need to access the message
        content with `message.content` instead of only `message`.

        ! if you want to recieve a **float** or an **int**, you must msg.content

        Returns a message object:
            msg.content:
                returns the message content string, int, float, ...
            msg:
                returns also the message content, but only as a string
            sender_group:
                returns the group name of the sender
            sender_id:
                returns the id of the sender
            topic:
                returns the topic

        Example::

         ... agent_01 ...
         self.messages('firm_01', 'potential_buyers', 'hello message')

         ... firm_01 - one subround later ...
         potential_buyers = get_messages('potential_buyers')
         for msg in potential_buyers:
            print('message: ', msg)
            print('message: ', msg.content)
            print('group name: ', msg.sender_group)
            print('sender id: ', msg.sender_id)
            print('topic: ', msg.topic)

        """
        try:
            shuffle(self._msgs[topic])
        except KeyError:
            self._msgs[topic] = []
        return self._msgs.pop(topic)

    def get_messages_all(self):
        """ returns all messages irregardless of the topic, in a dictionary by topic

        A message is a string with the message. You can also retrieve the sender
        by `message.sender_group` and `message.sender_id` and view the topic with
        'message.topic'. (see example)

        If you are sending a float or an integer you need to access the message
        content with `message.content` instead of only `message`.
        """
        ret = {}
        for key, messages in self._msgs.items():
            shuffle(messages)
            ret[key] = messages
        self._msgs.clear()
        return ret

    def _do_message_clearing(self, incomming_messages):
        """ agent receives all messages and objects that have been send in this
        subround and deletes the offers that where retracted, but not executed.

        '_o': registers a new offer
        '_d': delete received that the issuing agent retract
        '_p': clears a made offer that was accepted by the other agent
        '_r': deletes an offer that the other agent rejected
        '_g': recive a 'free' good from another party
        """
        for typ, msg in incomming_messages:
            if typ == '!b':
                self._open_offers_buy[msg.good][msg.id] = msg
            elif typ == '!s':
                self._open_offers_sell[msg.good][msg.id] = msg
            elif typ == '_p':
                offer = self._receive_accept(msg)
                if self.trade_logging == 2:
                    self._log_receive_accept_group(offer)
                elif self.trade_logging == 1:
                    self._log_receive_accept_agent(offer)
            elif typ == '_r':
                self._receive_reject(msg)
            elif typ == '_g':
                self._inventory.haves[msg[0]] += msg[1]
            elif typ == '_q':
                self._quotes[msg.id] = msg
            elif typ == '!o':
                self._contract_offers[msg.good].append(msg)
            elif typ == '_ac':
                contract = self._contract_offers_made.pop(msg.id)
                if contract.pay_group == self.group and contract.pay_id == self.id:
                    self._contracts_pay[contract.good][contract.id] = contract
                else:
                    self._contracts_deliver[contract.good][contract.id] = contract
            elif typ == '_dp':
                if msg.pay_group == self.group and msg.pay_id == self.id:
                    self._inventory[msg.good] += msg.quantity
                    self._contracts_pay[msg.good][msg.id].delivered.append(self.round)
                else:
                    self._inventory['money'] += msg.quantity * msg.price
                    self._contracts_deliver[msg.good][msg.id].paid.append(self.round)

            elif typ == '!d':
                if msg[0] == 'r':
                    del self._contracts_pay[msg[1]][msg[2]]
                if msg[0] == 'd':
                    del self._contracts_deliver[msg[1]][msg[2]]
            else:
                self._msgs.setdefault(typ, []).append(msg)
