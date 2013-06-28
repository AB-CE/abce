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
from __future__ import division
from random import shuffle


class Message():
    def __init__(self, msg):
        self.__dict__ = msg

    def __get__(self):
        return self.__dict__

    def __str__(self):
        return str(self.__dict__)

    def __getitem__(self, key):
        return self.__dict__[key]

    def __float__(self):
        return float(self.__dict__)

    def __int__(self):
        return int(self.__dict__)

class Messaging:
    def message(self, receiver_group, receiver_idn, topic, content):
        """ sends a message to agent. Agents receive it
        at the beginning of next round with :meth:`~abceagent.Messaging.get_messages` or
        :meth:`~abceagent.Messaging.get_messages_all`.

        See:
            message_to_group for messages to multiple agents

        Args::

         receiver_group: agent, agent_group or 'all'
         topic: string, with which this message can be received
         content: string, dictionary or class, that is send.

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
        msg = message(self.group, self.idn, receiver_group, receiver_idn, topic, content)
        self._send(receiver_group, receiver_idn, topic, msg)

    def message_to_group(self, receiver_group, topic, content):
        """ sends a message to agent, agent_group or 'all'. Agents receive it
        at the beginning of next round with :meth:`~abceagent.Messaging.get_messages` or
        :meth:`~abceagent.Messaging.get_messages_all`.

        Args::

         receiver_group: agent, agent_group or 'all'
         topic: string, with which this message can be received
         content: string, dictionary or class, that is send.

        Example::

            ... household_01 ...
            self.message('firm_01', 'quote_sell', {'good':'BRD', 'quantity': 5})

            ... firm_01 - one subround later ...
            requests = self.get_messages('quote_sell')
            for req in requests:
                self.sell(req.sender, req.good, reg.quantity, self.price[req.good])

        Example2::

         self.message('firm_01', 'm', "hello my message")

        """
        msg = message(self.group, self.idn, receiver_group, None, topic, content)
        self._send_to_group(receiver_group, topic, msg)


    def get_messages(self, topic='m'):
        """ self.messages() returns all new messages send with :meth:`~abceagent.Messaging.message`
        (topic='m'). The order is randomized. self.messages(topic) returns all
        messages with a topic.

        A message is a string with the message. You can also retrieve the sender
        by `message.sender_group` and `message.sender_idn` and view the topic with
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
            sender_idn:
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
            print('sender id: ', msg.sender_idn)
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
        by `message.sender_group` and `message.sender_idn` and view the topic with
        'message.topic'. (see example)

        If you are sending a float or an integer you need to access the message
        content with `message.content` instead of only `message`.
        """
        ret = self._msgs
        self._msgs = {}
        return ret

    def get_messages_biased(self, topic='m'):
        """ like self.messages(topic), but the order is not properly randomized, but
        it is faster. use whenever you are sure that the way you process messages
        is not affected by the order
        """
        try:
            return self._msgs.pop(topic)
        except KeyError:
            return []


def message(sender_group, sender_idn, receiver_group, receiver_idn, topic, content):
    msg = {}
    msg['sender_group'] = sender_group
    msg['sender_idn'] = sender_idn
    msg['receiver_group'] = receiver_group
    msg['receiver_idn'] = receiver_idn
    msg['topic'] = topic
    msg['content'] = content
    return msg
