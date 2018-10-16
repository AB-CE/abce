# Copyright 2012 Davoud Taghawi-Nejad
#
# Module Author: Davoud Taghawi-Nejad
#
# abcEconomics is open-source software. If you are using abcEconomics for your research you are
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
either be sent to an individual with :meth:`messenger.Messenger.message` or to a group with
:meth:`messenger.Messenger.message_to_group`. The receiving agent can either get all messages
with  :meth:`messenger.Messenger.get_messages_all` or messages with a specific topic with
:meth:`messenger.Messenger.get_messages`.
"""
from collections import defaultdict
from pprint import pprint
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


class Messenger:
    def __init__(self, id, agent_parameters, simulation_parameters):
        super(Messenger, self).__init__(id, agent_parameters, simulation_parameters)
        self._msgs = {}
        self.inbox = []
        self._out = []

    def send_envelope(self, receiver, topic, content):
        """ sends an envelope to the agent, the envelope contains the message (content),
        sender, receiver and topic. Agents receive it
        at the beginning of next round with :meth:`~abcEconomics.Messenger.get_messages` or
        :meth:`~abcEconomics.Messenger.get_messages_all`.

        The message that arrives has the following properties::
        message.sender
        message.receiver
        message.topic
        message.content

        Important the content, when received is in message.content

        Args::

            receiver:
                The name of the receiving agent a tuple (group, id).
                e.G. ('firm', 15)

            topic:
                string, with which this message can be received

            content:
                variable, tuple, dictionary or class, that is send.

        Example::

            ... household_01 ...
            self.send_envelope('firm', 01, 'quote_sell', {'good':'BRD', 'quantity': 5})

            ... firm_01 - one subround later ...

            requests = self.get_messages('quote_sell')
            for req in requests:
                self.make_offer(req.sender, req.content['good'], reg['quantity'], self.price[req.good])

        Example2::

         self.send_envelope('firm', 01, 'm', "hello my message")

        """
        msg = Message(sender=self.name,
                      receiver=receiver,
                      topic=topic,
                      content=content)
        self.send(receiver, topic, msg)

    def get_messages(self, topic='m'):
        """ self.get_messages() returns all new messages send with :meth:`~abcEconomics.Messenger.send`
        and :meth:`~abcEconomics.Messenger.send_envelope`. The order is randomized. self.get_messages(topic) returns all
        messages with a particular topic.

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
         self.send_envelope('firm_01', 'potential_buyers', 'hello message')

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

    def _do_message_clearing(self):
        """ agent receives all messages and objects that have been send in this
        subround and deletes the offers that where retracted, but not executed.

        '_d': delete received that the issuing agent retract
        'abcEconomics_receive_accept': clears a made offer that was accepted by the other agent
        'abcEconomics_receive_reject': deletes an offer that the other agent rejected
        'abcEconomics_receive_good': recive a 'free' good from another party
        """
        for typ, msg in self.inbox:
            if typ == 'abcEconomics_propose_buy':
                self._open_offers_buy[msg.good][msg.id] = msg
            elif typ == 'abcEconomics_propose_sell':
                self._open_offers_sell[msg.good][msg.id] = msg
            elif typ == 'abcEconomics_receive_accept':
                offer = self._receive_accept(msg)
                if self.trade_logging == 2:
                    self._log_receive_accept_group(offer)
                elif self.trade_logging == 1:
                    self._log_receive_accept_agent(offer)
            elif typ == 'abcEconomics_receive_reject':
                self._receive_reject(msg)
            elif typ == 'abcEconomics_receive_good':
                self._inventory.haves[msg[0]] += msg[1]
            elif typ == 'abcEconomics_receive_quote':
                self._quotes[msg.id] = msg
            elif typ == '!d':
                if msg[0] == 'r':
                    del self._contracts_pay[msg[1]][msg[2]]
                if msg[0] == 'd':
                    del self._contracts_deliver[msg[1]][msg[2]]
            elif typ == 'abcEconomics_forceexecute':
                getattr(self, msg[0])(*msg[1:])
            else:
                self._msgs.setdefault(typ, []).append(msg)
        self.inbox.clear()

    def _post_messages(self, agents):
        for name, envelope in self._out:
            try:
                agents[name].inbox.append(envelope)
            except KeyError:
                print(envelope)
                raise KeyError("Receiver %s does not exist" % str(name))
        self._out.clear()

    def _post_messages_multiprocessing(self, num_processes):
        out = self._out
        self._out = defaultdict(list)
        return out

    def send(self, receiver, topic, msg):
        """ sends a message to a receiver
        The agents receives it at the begin of each subround.

        Args:

        sends a message to agent. Agents receive it
        at the beginning of next round with :meth:`~abcEconomics.Messenger.get_messages`(topic) or
        :meth:`~abcEconomics.Messenger.get_messages_all`.

        Args:
            receiver:
                to whom to send the message
            topic:
                topic, under which to receive the message
            msg:
                Some datatype with a message


        Example::

            ... household_01 ...
            self.send(('firm', 01), 'quote_sell', {'good':'BRD', 'quantity': 5, 'sender': self.name})

            ... firm_01 - one subround later ...

            requests = self.get_messages('quote_sell')

            for req in requests:
                self.make_offer(req['sender'], req['good'], reg['quantity'], self.price[req.good])

        Example2::

         self.send(('firm', 01), 'm', "hello my message")

        """
        self._out.append((receiver, (topic, msg)))

    def _send_multiprocessing(self, receiver, typ, msg):
        """ Is used to overwrite _send in multiprocessing mode.
        Requires that self._out is overwritten with a defaultdict(list) """
        self._out[hash(receiver) % self._processes].append(
            (receiver, (typ, msg)))

    def check_for_lost_messages(self):
        """ Checks whether there are any messages, or trade requests that have not been
        processed """
        for offer in list(self.given_offers.values()):
            if offer.made < self.time:
                print("in agent %s this offers have not been retrieved:" %
                      self.name_without_colon)
                for offer in list(self.given_offers.values()):
                    if offer.made < self.time:
                        print(offer.__repr__())
                raise Exception('%s_%i: There are offers have been made before'
                                'last round and not been retrieved in this'
                                'round get_offer(.)' % (self.group, self.id))

        if sum([len(offers) for offers in list(self._open_offers_buy.values())]):
            pprint(dict(self._open_offers_buy))
            raise Exception('%s_%i: There are offers an agent send that have '
                            'not been retrieved in this round get_offer(.)' %
                            (self.group, self.id))

        if sum([len(offers) for offers in list(self._open_offers_sell.values())]):
            pprint(dict(self._open_offers_sell))
            raise Exception('%s_%i: There are offers an agent send that have '
                            'not been retrieved in this round get_offer(.)' %
                            (self.group, self.id))

        if sum([len(offers) for offers in list(self._msgs.values())]):
            pprint(dict(self._msgs))
            raise Exception('(%s, %i): There are messages an agent send that '
                            'have not been retrieved in this round '
                            'get_messages(.)' % (self.group, self.id))
