""" must be imported with ' from agentengine import * ' by all agents """
import zmq
import multiprocessing
from abce_common import agent_name, group_address
from inspect import getmembers, ismethod
from random import shuffle
import compiler
import pyparsing as pp

class AgentEngine(multiprocessing.Process):
    """ must be inherited by all agents as first line in def ' __init__(self)':
    (see agent.py prototype)
    """
    def __init__(self, idn, group_name, __command_addresse):
        multiprocessing.Process.__init__(self)
        self.idn = idn
        self.name = agent_name(group_name, idn)
        self.group_name = group_name
        #TODO should be group_address(group_name), but it would not work
        # when fired manual + ':' and manual group_address need to be removed
        self._del_given_offers_end_subround = []
        self.__command_addresse = __command_addresse
        self.__methods__ = {}
        self._register_actions()

        self._haves = {}
        self._haves['money'] = 0
        self._msgs = {}

        self.given_offers = {}
        self._open_offers = {}
        self._offer_count = 0

        self.round = 0

    def _register_actions(self):
        """ registers all actions of the Agent, which do not start with '_' """
        for method in getmembers(self):
            if (ismethod(method[1]) and
                    not(method[0] in vars(AgentEngine) or method[0].startswith('_') or method[0] in vars(multiprocessing.Process))):
                self.__methods__[method[0]] = method[1]
            self.__methods__['_end_of_subround_clearing'] = self._end_of_subround_clearing
            self.__methods__['_produce_resource_rent_and_labor'] = self._produce_resource_rent_and_labor
            self.__methods__['_db_haves'] = self._db_haves
            self.__methods__['_advance_round'] = self._advance_round
            #TODO inherited classes provide methods that should not be callable
            #change _ policy _ callable from outside __ not and exception lists

    def run(self):
        """ internal """
        context = zmq.Context()
        self.commands = context.socket(zmq.SUB)
        self.commands.connect(self.__command_addresse)
        self.commands.setsockopt(zmq.SUBSCRIBE, "all")
        self.commands.setsockopt(zmq.SUBSCRIBE, self.name)
        self.commands.setsockopt(zmq.SUBSCRIBE, group_address(self.group_name))

        self.out = context.socket(zmq.PUSH)
        self.out.connect("ipc://frontend.ipc")
        self.in_sok = context.socket(zmq.SUB)
        self.in_sok.connect("ipc://backend.ipc")
        self.in_sok.setsockopt(zmq.SUBSCRIBE, "all")
        self.in_sok.setsockopt(zmq.SUBSCRIBE, self.name)
        self.in_sok.setsockopt(zmq.SUBSCRIBE, group_address(self.group_name))
        self.__signal_finished()
        self._loop()

    def _loop(self):
        while True:
            msg = self.commands.recv()
            command = self.commands.recv()
            if command == "!":
                subcommand = self.commands.recv()
                if subcommand == 'die':
                    self.__signal_finished()
                    break
                elif subcommand == 'follow':
                    self._loop_protocol()
                    break
            try:
                self.__methods__[command]()
            except KeyError:
                if command not in self.__methods__:
                    raise SystemExit(command + ' not declared (' + self.name + ' in agent.py)')
                else:
                    raise
            self.__signal_finished()

    def _loop_protocol(self):
        while True:
            msg = self.commands.recv()
            command = self.commands.recv()
            if command == "!":
                subcommand = self.commands.recv()
                if subcommand == 'die':
                    self.__signal_finished()
                    break
            try:
                self.__methods__[command]()
            except KeyError:
                if command not in self.__methods__:
                    raise SystemExit(command + ' not declared (' + self.name + ' in agent.py)')
                else:
                    raise
                raise SystemExit
            if command[0] != '_':
                self._follow(command)
            self.__signal_finished()

    def _produce_resource_rent_and_labor(self):
        resource, units, product = self.commands.recv_multipart()
        if resource in self._haves:
            try:
                self._haves[product] += float(units) * self._haves[resource]
            except KeyError:
                self._haves[product] = float(units) * self._haves[resource]

    def _db_haves(self):
        command = self.commands.recv()
        try:
            data_to_track = self.__methods__[command]()
        except KeyError:
            data_to_track = self._haves
        self._send("db_agent:" + command + ":" + self.group_name, str(self.idn), data_to_track)


    def _follow(self, last_command):
        self.out.send("db_agent:" + self.group_name + ':', zmq.SNDMORE)
        self.out.send(self.name, zmq.SNDMORE)
        self.out.send(last_command, zmq.SNDMORE)
        try:
            self.out.send_json(self.follow())
        except AttributeError:
            SystemExit('AttributeError: You are probably accessing a variabe'
                    'that does not yet exist. Put self.variable_name = None'
                    'into the __init__(...) method.')

    def follow(self):
        """ You can implement this fuction in your agent to track the changes
        of an agents variables or goods after each subround. If you do not
        implement this function the goods an agent owns are tracked. You track
        an agent by declaring in start.py: w.follow_agent('agent', id_number)

        You have to write a function that returns a dictionary. This dictionary
        will be tracked in the database.

        Example::

         start.py:
            ...
            w.follow_agent('firm', i)
            w.run

        agent.py:
         def follow(self):
            track = {}  # track is a dictionary
            track.update(self._haves)  # adds all goods of the agent to the dict
            track['knows_neighbor'] = self.knows_neighbor
            track['last_round_price'] = self.last_round_price
            return track  # essential line

        Because follow tracks from the beginnig on it might be necessary to
        set variable to None or any value in the __init__(...) method. E.G.
        self.last_round_price = 0; self.knows_neighbor = None
        """
        return self._haves

    def _db_dicts(self):
        command = self.commands.recv()
        variables = self.commands.recv()
        ','.join([key + ',' + str(value) for key, value in self.__dict__[variables].items()])
        self._send("db_agent:", command + ":" + self.group_name, self.idn, haves)

    def _db_variable(self):
        command = self.commands.recv()
        variable = self.commands.recv()
        self._send("db_agent:", command + ":" + self.group_name, self.idn, self.__dict__[variable])

    def _end_of_subround_clearing(self):
        """ agent recieves all messages and objects that have been send in this
        subround and deletes the offers that where retracted, but not executed.

        '_o': registers a new offer
        '_d': delete recieved that the issuing agent retract
        '_a': clears a made offer that was acceped by the other agent
        '_r': deletes an offer that the other agent rejected
        """
        while True:
            address = self.in_sok.recv()
            if address == 'all.':
                break
            typ = self.in_sok.recv()
            msg = self.in_sok.recv_json()
            if   typ == '_o':
                self._open_offers[msg['idn']] = msg
                #TODO make self._open_offers a pointer to _msgs['_o']
                #TODO make different lists for sell and buy offers
            elif typ == '_d':
                del self._open_offers[msg]
            elif typ == '_a':
                self._recieve_accept(msg)
            elif typ == '_p':
                self._recieve_partial_accept(msg)
            elif typ == '_r':
                self._delete_given_offer(msg)
            else:
                self._msgs.setdefault(typ, []).append(msg)
        for offer_id in self._del_given_offers_end_subround:
            try:
                self._delete_given_offer(offer_id)
            except KeyError:
                pass
        self._del_given_offers_end_subround = []

    def messages(self, typ='m'):
        """ self.messages() returns all new messages send before this step
        (typ='m'). The order is randomized self.messages(typ) returns all
        messages with a particular non standard type typ e.G. 'n'.
        The order of the messages is randomized.

        Example::

         potential_buyers = self.messages('address')
         for p_buyer in potential_buyers:
            print(p_buyer)
        """
        try:
            shuffle(self._msgs[typ])
        except KeyError:
            self._msgs[typ] = []
        return self._msgs.pop(typ)

    def messages_biased(self, typ='m'):
        """ like self.messages(typ), but the order is not properly randomized, but
        its faster. use whenever you are sure that the way you process messages
        is not affected by the order
        """
        try:
            return self._msgs.pop(typ)
        except KeyError:
            return []

    def get_quotes(self):
        """ self.quotes() returns all new quotes and removes them. The order
        is randomized.

        Example::

         quotes = self.get_quotes()

        Returns::
         list of quotes
        """
        if 'q' not in self._msgs:
            return []
        shuffle(self._msgs['q'])
        return self._msgs.pop('q')

    def get_quotes_biased(self):
        """ like self.quotes(), but the order is not randomized, so
        its faster.

        self.quotes() returns all new quotes and removes them. The order
        is randomized.

        Use whenever you are sure that the way you process messages
        is not affected by the order.
        """
        if 'q' in self._msgs:
            return self._msgs.pop('q')
        else:
            return []

    def accept_quote(self, quote):
        """ makes a commited buy or sell out of the counterparties quote

        Args::
         quote: buy or sell quote that is acceped

        """
        if quote['buysell'] == 'qs':
            self.buy(quote['sender'], quote['good'], quote['quantity'], quote['price'])
        else:
            self.sell(quote['sender'], quote['good'], quote['quantity'], quote['price'])

    def accept_quote_partial(self, quote, quantity):
        """ makes a commited buy or sell out of the counterparties quote

        Args::
         quote: buy or sell quote that is acceped
         quantity: the quantity that is offered/requested
         it should be less than propsed in the quote, but this is not enforced.

        """
        if quote['buysell'] == 'qs':
            self.buy(quote['sender'], quote['good'], quantity, quote['price'])
        else:
            self.sell(quote['sender'], quote['good'], quantity, quote['price'])

    #TODO delete and create assert unanswered offers
    def assert_empty_messages(self):
        """ this method can be used to make sure that at the end of a round no
        recieved messages are in the que"""
        messages = self.messages()
        if messages:
            raise SystemExit("MESSAGE Q NOT EMPTHY" + messages)

    def open_offers_all(self):
        """ returns all open offers, without deleting them """
        return self._open_offers.values()

    def open_offers(self, good):
        """ returns all open offers of the 'good', without deleting them """
        def func(offer):
            if offer['good'] == good:
                return True
        return filter(func, self._open_offers.values())
        #TODO unbeautiful

    def __signal_finished(self):
        """ signals modelswarm via communication that the agent has send all
        messages and finish his action """
        self.out.send_multipart(['!', '.'])

    def _send_class(self, receiver, typ, msg):
        """ sends a class """
        self._send(receiver, typ, msg.__dict__)

    def _send(self, receiver, typ, msg):
        """ sends a message to 'receiver', who can be an agent, a group or
        'all'. The agents receives it at the begin of each round in
        self.messages(typ) is 'm' for mails.
        typ =(_o,c,u,r) are
        reserved for internally processed offers.
        """
        self.out.send(receiver, zmq.SNDMORE)
        self.out.send(typ, zmq.SNDMORE)
        self.out.send_json(msg)
    #TODO public way of sending messages and objects
    def mail(self, receiver, message):
        """ sends a message to agent, agent_group or 'all'. Agents receive it
        at the beginning of next round in self.messages()
        """
        self._send(receiver, 'm', message)

    def send_address(self, receiver, name):
        """ Sends some agent's name ore agents group's address under which these
        agents recieve messages and objects to reciever (agent or group)

        agents can receive addresses with:

        `potential_buyers = self.messages('address')`
        """
        self._send(receiver, 'address', name)

    def send_my_address(self, receiver, typ='address'):
        """ Sends the agents own name under which the agents recieves messages
        and objects to reciever (agent or group)

        agents can receive addresses with:

        `potential_buyers = self.messages('address')`
        """
        self._send(receiver, typ, self.name)

    def count(self, good):
        """ returns how much of good an agent has (0 when unknown) """
        try:
            return self._haves[good]
        except KeyError:
            return 0

    def _offer_counter(self):
        """ returns a uniqe number for an offer (containing the agent's name)
        """
        self._offer_count += 1
        return str(self.name) + str(self._offer_count)

    def _advance_round(self):
        self.round += 1

    def quote_sell(self, receiver, good, quantity, price):
        """ quotes a price to sell quantity of 'good' to receiver

        price (money) per unit
        offers a deal without checking or committing resources

        Args:
            receiver: an agent name a group of agents on 'all'
            (names and group names can be generated with
            agent_name(group_name, id) and group_address(group_name))
            'good': name of the good
            quantity: maximum units disposed to sell at this price
            price: price per unit
        """
        offer = Offer(self.name, receiver, good, quantity, price, 'qs')
        self._send_class(receiver, 'q', offer)
        return offer

    def quote_buy(self, receiver, good, quantity, price):
        """ quotes a price to buy quantity of 'good' to receiver

        price (money) per unit
        offers a deal without checking or committing resources

        Args:
            receiver: an agent name a group of agents on 'all'
            (names and group names can be generated with
            agent_name(group_name, id) and group_address(group_name))
            'good': name of the good
            quantity: maximum units disposed to buy at this price
            price: price per unit
        """
        offer = Offer(self.name, receiver, good, quantity, price, 'qb')
        self._send_class(receiver, 'q', offer)
        return offer

    def sell(self, receiver, good, quantity, price):
        """ commits to sell the quantity of good at price

        The goods are not in haves or self.count(). When the offer is
        rejected they are automatically reacreditated. When the offer is
        accepted the money amount is accreditated. (partial acceptance
        accordingly)

        Args:
            receiver: an agent name  NEVER a group or 'all'!!!
            (its an error but with a confusing warning)
            'good': name of the good
            quantity: maximum units disposed to buy at this price
            price: price per unit
        """
        try:
            if self._haves[good] < quantity:
                raise NotEnoughGoods(self.name, good, quantity - self._haves[good])
        except KeyError:
            raise GoodDoesNotExist(self.name, good)

        self._haves[good] -= quantity
        offer = Offer(self.name, receiver, good, quantity, price, buysell='s', idn=self._offer_counter())
        self._send_class(receiver, '_o', offer)
        self.given_offers[offer.idn] = offer
        return offer


    def buy(self, receiver, good, quantity, price):
        """ commits to sell the quantity of good at price

        The goods are not in haves or self.count(). When the offer is
        rejected they are automatically reacreditated. When the offer is
        accepted the money amount is accreditated. (partial acceptance
        accordingly)

        Args:
            receiver: an agent name  NEVER a group or 'all'!!!
            (its an error but with a confusing warning)
            'good': name of the good
            quantity: maximum units disposed to buy at this price
            price: price per unit
        """
        money_amount = quantity * price
        if self._haves['money'] < money_amount:
            raise NotEnoughGoods(self.name, 'money', money_amount - self._haves['money'])

        self._haves['money'] -= money_amount
        offer = Offer(self.name, receiver, good, quantity, price, 'b', self._offer_counter())
        self._send_class(receiver, '_o', offer)
        self.given_offers[offer.idn] = offer
        return offer

    def retract(self, offer):
        """ The agent who made a buy or sell offer can retract it

        The offer an agent made is deleted at the end of the subround and the
        committeg good reapears in the haves. Howevery if another agent
        accepts in the same round the trade will be cleared and not retracted.

        Args:
            offer: the offer he made with buy or sell
            (offer not quote!)
        """
        self._send(offer.receiver, '_d', offer.idn)
        self._del_given_offers_end_subround.append(offer.idn)

    def accept(self, offer):
        ##TODO needs a whole bunch of trys to avoid KeyError
        """ The offer is accepted and cleared

        Args::

            offer: the offer the other party made
            (offer not quote!)
        """
        money_amount = offer['quantity'] * offer['price']
        if offer['buysell'] == 's':
            if self._haves['money'] < money_amount:
                self.reject(offer)
                raise NotEnoughGoods(self.name, 'money', money_amount - self._haves['money'])
            try:
                self._haves[offer['good']] += offer['quantity']
            except KeyError:
                self._haves[offer['good']] = offer['quantity']
            self._haves['money'] -= offer['quantity'] * offer['price']
        else:
            try:
                if self._haves[offer['good']] < offer['quantity']:
                    self.reject(offer)
                    raise NotEnoughGoods(self.name, offer['good'], offer['quantity'] - self._haves[offer['good']])
            except KeyError:
                if offer['good'] not in self._haves:
                    raise GoodDoesNotExist(self.name, offer['good'])
                else:
                    raise KeyError
            self._haves[offer['good']] -= offer['quantity']
            self._haves['money'] += offer['quantity'] * offer['price']
        self._send(offer['sender'], '_a', offer['idn'])
        del self._open_offers[offer['idn']]

    def accept_partial(self, offer, percentage):
        """ TODO The offer is partly accepted and cleared

        Args:
            offer: the offer the other party made
            (offer not quote!)
        """
        pass

    def reject(self, offer):
        """ The offer is rejected

        Args:
            offer: the offer the other party made
            (offer not quote!)
        """
        self._send(offer['sender'], '_r', offer['idn'])
        del self._open_offers[offer['idn']]

    def _recieve_accept(self, offer_id):
        """ When the other party accepted the  money or good is recieved
        and the offer deleted
        """
        offer = self.given_offers.pop(offer_id)
        if offer.buysell == 's':
            try:
                self._haves['money'] += offer.quantity * offer.price
            except KeyError:
                self._haves['money'] = offer.quantity * offer.price
        else:
            try:
                self._haves[offer.good] += offer.quantity
            except KeyError:
                self._haves[offer.good] = offer.quantity


    def _recieve_partial_accept(self, offer_id):
        """ When the other party partially accepted the  money or good is
        recieved, remaining good or money is added back to haves and the offer
        is deleted
        """
        pass

    def _delete_given_offer(self, offer_id):
        """ delets a given offer

        is used by _end_of_subround_clearing, when the other party rejects
        or at the end of the subround when agent retracted the offer

        """
        offer = self.given_offers.pop(offer_id)
        if offer.buysell == 's':
            self._haves[offer.good] += offer.quantity
        else:
            self._haves['money'] += offer.quantity * offer.price

    def create(self, good, quantity):
        """ creates quantity of the good out of nothing

        Use this create with care, as long as you use it only for labor and
        natural resources your model is macroeconomally complete.

        Args:
            'good': is the name of the good
            quantity: number
        """
        try:
            self._haves[good] += quantity
        except KeyError:
            self._haves[good] = quantity

    def _destroy(self, good, quantity):
        """ destroys quantity of the good,

        Args::

            'good': is the name of the good
            quantity: number

        Raises::

            NotEnoughGoods: when goods are insufficient
            GoodDoesNotExist: when good does not exist for this agent
        """
        try:
            self._haves[good] -= quantity
        except KeyError:
            raise GoodDoesNotExist(self.name, good)
        if self._haves[good] < 0:
            self._haves[good] = 0
            raise NotEnoughGoods

    def _destroy_all(self, good):
        """ destroys all of the good, returns how much

        Args::

            'good': is the name of the good

        Raises::

            GoodDoesNotExist: when good does not exist for this agent
        """
        try:
            quantity_destroyed = self._haves[good]
        except KeyError:
            raise GoodDoesNotExist(self.name, good)
        self._haves[good] = 0
        return quantity_destroyed


class Firm:
    def produce_use_everything(self, production_function):
        """ Produces output goods from all input goods, used in this
        production_function, the agent owns.

        Args::

            production_function: A production_function produced with
            :ref:`create_production_function`, :ref:`create_cobb_douglas` or
            :ref:`create_leontief`

        Raises::

            GoodDoesNotExist: This is raised when unknown goods are used.

        Example::

            self.produce(car_production_function)
        """
        self.produce(production_function, dict((inp, self._haves) for inp in production_function['input']))

    def produce(self, production_function, input_goods):
        """ Produces output goods given the specified amount of inputs.

        Transforms the Agent's goods specified in input goods
        according to a given production_function to output goods.
        Automatically changes the agent's belonging. Raises an
        exception, when the agent does not have sufficient resources.

        Args:
            production_function: A production_function produced with
            :ref:`create_production_function`, :ref:`create_cobb_douglas` or
            :ref:`create_leontief`
            {'input_good1': amount1, 'input_good2': amount2 ...}: dictionary
            containing the amount of input good used for the production.

        Raises:
            NotEnoughGoods: This is raised when the goods are insufficient.
            GoodDoesNotExist: This is raised when unknown goods are used.

        Example::

            self.car = {'tire': 4, 'metal': 2000, 'plastic':  40}
            self.bike = {'tire': 2, 'metal': 400, 'plastic':  20}
            try:
                self.produce(car_production_function, self.car)
            except NotEnoughGoods:
                A.produce(bike_production_function, self.bike)
        """
        for good in production_function['input']:
            try:
                if self._haves[good] < input_goods[good]:
                    raise NotEnoughGoods(self.name, good, production_function['input'][good] - self._haves[good])
            except KeyError:
                raise GoodDoesNotExist(self.name, good)
        for good in production_function['input']:
            self._haves[good] -= input_goods[good]
        goods_vector = input_goods.copy()
        for good in production_function['output']:
            goods_vector[good] = None
        exec(production_function['formula'], {}, goods_vector)
        for good in production_function['output']:
            try:
                self._haves[good] += goods_vector[good]
            except KeyError:
                self._haves[good] = goods_vector[good]

    def sufficient_goods(self, input_goods):
        """ checks whether the agent has all the goods in the vector input """
        for good in input_goods:
            try:
                if self._haves[good] < input_goods[good]:
                    raise NotEnoughGoods(self.name, good, input_goods[good] - self._haves[good])
            except KeyError:
                raise GoodDoesNotExist(self.name, good)


def create_production_function(formula, typ='from_formula'):
    """ creates a production function from formula

    A production function is a produceation process that produces the
    given input given input goods according to the formula to the output
    goods.
    Production_functions are than used as an argument in produce,
    predict_vector_produce and predict_output_produce.

    create_production_function_fast is faster but more complicated

    Args:
        "formula": equation or set of equations that describe the
        production process. (string) Several equation are seperated by a ;

    Returns:
        A production_function that can be used in produce etc.

    Example:
        formula = 'golf_ball = (ball) * (paint / 2); waste = 0.1 * paint'
        self.production_function = create_production_function(formula, 'golf', 'waste')
        self.produce(self.production_function, {'ball' : 1, 'paint' : 2}

    //exponential is ** not ^
    """
    parse_single_output = pp.Word(pp.alphas+"_", pp.alphanums+"_") + pp.Suppress('=') + pp.Suppress(pp.Word(pp.alphanums + '*/+-().[]{} '))
    parse_output = pp.delimitedList(parse_single_output, ';')
    parse_single_input = pp.Suppress(pp.Word(pp.alphas+"_", pp.alphanums+"_")) + pp.Suppress('=') \
            + pp.OneOrMore(pp.Suppress(pp.Optional(pp.Word(pp.nums + '*/+-().[]{} '))) + pp.Word(pp.alphas+"_", pp.alphanums+"_"))
    parse_input = pp.delimitedList(parse_single_input, ';')

    production_function = {}
    production_function['type'] = typ
    production_function['parameters'] = formula
    production_function['formula'] = compiler.compile(formula, '<string>', 'exec')
    production_function['output'] = list(parse_output.parseString(formula))
    production_function['input']= list(parse_input.parseString(formula))
    return production_function

def create_production_function_fast(formula, output_goods, input_goods, typ='from_formula'):
    """ creates a production function from formula, with given outputs

    A production function is a producetion process that produces the
    given input given input goods according to the formula to the output
    goods.
    Production_functions are than used as an argument in produce,
    predict_vector_produce and predict_output_produce.

    Args:
        "formula": equation or set of equations that describe the
        production process. (string) Several equation are seperated by a ;
        [output]: list of all output goods (left hand sides of the equations)

    Returns:
        A production_function that can be used in produce etc.

    Example:
        formula = 'golf_ball = (ball) * (paint / 2); waste = 0.1 * paint'
        self.production_function = create_production_function(formula, 'golf', 'waste')
        self.produce(self.production_function, {'ball' : 1, 'paint' : 2}

    //exponential is ** not ^
    """
    production_function = {}
    production_function['type'] = typ
    production_function['parameters'] = formula
    production_function['formula'] = compiler.compile(formula, '<string>', 'exec')
    production_function['output'] = output_goods
    production_function['input'] = input_goods
    return production_function


def create_cobb_douglas(output, multiplier, exponents):
    """ creates a Cobb-Douglas production function

    A production function is a produceation process that produces the
    given input given input goods according to the formula to the output
    good.
    Production_functions are than used as an argument in produce,
    predict_vector_produce and predict_output_produce.

    Args:
        'output': Name of the output good
        multiplier: Cobb-Douglas multiplier
        {'input1': exponent1, 'input2': exponent2 ...}: dictionary
        containing good names 'input' and correstponding exponents
    Returns:
        A production_function that can be used in produce etc.

    Example:
    self.plastic_production_function = create_cobb_douglas('plastic', {'oil' : 10, 'labor' : 1}, 0.000001)
    self.produce(self.plastic_production_function, {'oil' : 20, 'labor' : 1})

    """
    formula = output + '=' + str(multiplier) + '*' + ('*'.join(['**'.join([input_good, str(input_quantity)]) for input_good, input_quantity in exponents.iteritems()]))
    production_function = {}
    production_function['type'] = 'cobb-douglas'
    production_function['parameters'] = exponents
    production_function['multiplier'] = multiplier
    production_function['formula'] = compiler.compile(formula, '<string>', 'exec')
    production_function['output'] = [output]
    production_function['input'] = [input_good for input_good in exponents]
    return production_function


def create_leontief(output, utilization_quantities, multiplier=1, isinteger='int'):
    """ creates a Leontief production function

    A production function is a produceation process that produces the
    given input given input goods according to the formula to the output
    good.
    Production_functions are than used as an argument in produce,
    predict_vector_produce and predict_output_produce.

    Warning, when you produce with a Leontief production_function all goods you
    put in the produce(...) function are used up. Regardless whether it is an
    efficient or wastefull bundle

    Args:
        'output': Name of the output good
        {'input1': utilization_quantity1, 'input2': utilization_quantity2 ...}: dictionary
        containing good names 'input' and correstponding exponents
        multiplier: multipler
        isinteger='int' or isinteger='': When 'int' produce only integer
        amounts of the good. When '', produces floating amounts.

, str(input_quantity)
    Returns:
        A production_function that can be used in produce etc.

    Example:
    self.car_technology = create_leontief('car', {'tire' : 4, 'metal' : 1000, 'plastic' : 20}, 1)
    two_cars = {'tire': 8, 'metal': 2000, 'plastic':  40}
    self.produce(self.car_technology, two_cars)
    """
    i = utilization_quantities.iteritems()
    #formula = output + '=' + str(multiplier) + '*' + ('*'.join(['**'.join([input_good, str(input_quantity)]) for input_good, input_quantity in i ]))
    multiples = ','.join([input_good + '/' + str(float(input_quantity)) for input_good, input_quantity in i])
    formula = output + ' = ' + str(multiplier) + ' * ' + isinteger + '(min([' + multiples + ']))'
    production_function = {}
    production_function['type'] = 'leontief'
    production_function['parameters'] = utilization_quantities
    production_function['multiplier'] = multiplier
    production_function['isinteger'] = isinteger
    production_function['formula'] = compiler.compile(formula, '<string>', 'exec')
    production_function['output'] = [output]
    production_function['input'] = [input_good for input_good in utilization_quantities]
    return production_function


def predict_produce_output(production_function, input_goods):
    """ Calculates the output of a production (but does not preduce)

        Predicts the production of produce(production_function, input_goods)
        see also: Predict_produce(.) as it returns a calculatable vector

    Args:
        production_function: A production_function produced with
        create_production_function, create_cobb_douglas or create_leontief
        {'input_good1': amount1, 'input_good2': amount2 ...}: dictionary
        containing the amount of input good used for the production.

    Example::

        print(A.predict_output_produce(car_production_function, two_cars))
        >>> {'car': 2}

    """
    goods_vector = input_goods.copy()
    for good in production_function['output']:
        goods_vector[good] = None
    exec(production_function['formula'], {}, goods_vector)
    output = {}
    for good in production_function['output']:
        output[good] = goods_vector[good]
    return output


def predict_produce(production_function, input_goods):
    """ Returns a vector with input (negative) and output (positive) goods

        Predicts the production of produce(production_function, input_goods) and
        the use of input goods.
        net_value(.) uses a price_vector (dictionary) to calculate the
        net value of this production.

    Args:
        production_function: A production_function produced with
        create_production_function, create_cobb_douglas or create_leontief
        {'input_good1': amount1, 'input_good2': amount2 ...}: dictionary
        containing the amount of input good used for the production.

    Example::

     prices = {'car': 50000, 'tire': 100, 'metal': 10, 'plastic':  0.5}
     value_one_car = net_value(predict_produce(car_production_function, one_car), prices)
     value_two_cars = net_value(predict_produce(car_production_function, two_cars), prices)
     if value_one_car > value_two_cars:
        A.produce(car_production_function, one_car)
     else:
        A.produce(car_production_function, two_cars)
    """
    goods_vector = input_goods.copy()
    for good in production_function['output']:
        goods_vector[good] = None
    exec(production_function['formula'], {}, goods_vector)
    for goods in production_function['output']:
        result[good] = goods_vector[good]
    for goods in production_function['input']:
        result[good] = -goods_vector[good]
    return result


def net_value(goods_vector, price_vector):
    """ Calculates the net_value of a goods_vector given a price_vector

        goods_vectors are vector, where the input goods are negative and
        the output goods are positive. When we multiply every good with its
        according price we can calculate the net_value of the correstponding
        production.
        goods_vectors are produced by predict_produce(.)


    Args:
        goods_vector: a dictionary with goods and quantities
        e.G. {'car': 1, 'metal': -1200, 'tire': -4, 'plastic': -21}
        price_vector: a dictionary with goods and prices (see example)

    Example::

     prices = {'car': 50000, 'tire': 100, 'metal': 10, 'plastic':  0.5}
     value_one_car = net_value(predict_produce(car_production_function, one_car), prices)
     value_two_cars = net_value(predict_produce(car_production_function, two_cars), prices)
     if value_one_car > value_two_cars:
        produce(car_production_function, one_car)
     else:
        produce(car_production_function, two_cars)
    """
    ret = 0
    for good, quantity in goods_vector.items():
        ret += price_vector[good] * quantity
    return ret

class Household:
    def utility_function(self):
        """ the utility function should be created with:
        create_cobb_douglas_utility_function,
        create_utility_function or
        create_utility_function_fast
        """
        return self._utility_functionconsume_all

    def consume_everything(self):
        """ consumes everything that is in the utility function
        returns utility according consumption

        Args::

            utility_function: A utility_function produced with
            :ref:`create_utility_function`,
            :ref:`create_cobb_douglas_utility_function` or

        Raises::
            GoodDoesNotExist: This is raised when unknown goods are used.

        Example::

            self.consume_everything()
        """
        try:
            return self.consume(dict((inp, self._haves[inp]) for inp in self._utility_function['input']))
        except KeyError:
            raise GoodDoesNotExist(self.name, '*')

    def consume(self, input_goods):
        """ consumes input_goods returns utility according consumption

        Args:
            {'input_good1': amount1, 'input_good2': amount2 ...}: dictionary
            containing the amount of input good consumed.

        Raises:
            NotEnoughGoods: This is raised when the goods are insufficient.
            GoodDoesNotExist: This is raised when unknown goods are used.

        Example::

            self.consumption_set = {'car': 1, 'ball': 2000, 'bike':  2}
            try:
                self.consume(utility_function, self.consumption_set)
            except NotEnoughGoods:
                self.consume(utility_function, self.smaller_consumption_set)
        """
        for good in self._utility_function['input']:
            try:
                if self._haves[good] < input_goods[good]:
                    raise NotEnoughGoods(self.name, good, self._utility_function['input'][good] - self._haves[good])
            except KeyError:
                raise GoodDoesNotExist(self.name, good)
        for good in self._utility_function['input']:
            self._haves[good] -= input_goods[good]
        goods_vector = input_goods.copy()
        goods_vector['utility'] = None
        exec(self._utility_function['formula'], {}, goods_vector)
        return goods_vector['utility']


    def set_utility_function(formula, typ='from_formula'):
        """ creates a utility function from formula

        Utility_functions are than used as an argument in consume_with_utility,
        predict_utility and predict_utility_and_consumption.

        create_utility_function_fast is faster but more complicatedutility_function

        Args:
            "formula": equation or set of equations that describe the
            utility function. (string) needs to start with 'utility = ...'

        Returns:
            A utility_function

        Example:
            formula = 'utility = ball + paint'
            self._utility_function = create_utility_function(formula)
            self.consume_with_utility(self._utility_function, {'ball' : 1, 'paint' : 2})

        //exponential is ** not ^
        """
        parse_single_input = pp.Suppress(pp.Word(pp.alphas+"_", pp.alphanums+"_")) + pp.Suppress('=') \
                + pp.OneOrMore(pp.Suppress(pp.Optional(pp.Word(pp.nums + '*/+-().[]{} ')))
                + pp.Word(pp.alphas+"_", pp.alphanums+"_"))
        parse_input = pp.delimitedList(parse_single_input, ';')

        self._utility_function = {}
        self._utility_function['type'] = typ
        self._utility_function['parameters'] = formula
        self._utility_function['formula'] = compiler.compile(formula, '<string>', 'exec')
        self._utility_function['input']= list(parse_input.parseString(formula))


    def set_utility_function_fast(formula, input_goods, typ='from_formula'):
        """ creates a utility function from formula

        Utility_functions are than used as an argument in consume_with_utility,
        predict_utility and predict_utility_and_consumption.

        create_utility_function_fast is faster but more complicated

        Args:
            "formula": equation or set of equations that describe the
            production process. (string) Several equation are seperated by a ;
            [output]: list of all output goods (left hand sides of the equations)

        Returns:
            A utility_function that can be used in produce etc.

        Example:
            formula = 'utility = ball + paint'

            self._utility_function = create_utility_function(formula, ['ball', 'paint'])
            self.consume_with_utility(self._utility_function, {'ball' : 1, 'paint' : 2}

        //exponential is ** not ^
        """
        self._utility_function = {}
        self._utility_function['type'] = typ
        self._utility_function['parameters'] = formula
        self._utility_function['formula'] = compiler.compile(formula, '<string>', 'exec')
        self._utility_function['input'] = input_goods


    def set_cobb_douglas_utility_function(self, multiplier, exponents):
        """ creates a Cobb-Douglas utility function

        Utility_functions are than used as an argument in consume_with_utility,
        predict_utility and predict_utility_and_consumption.

        Args:
            {'input1': exponent1, 'input2': exponent2 ...}: dictionary
            containing good names 'input' and correstponding exponents
        Returns:
            A utility_function that can be used in consume_with_utility etc.

        Example:
        self._utility_function = create_cobb_douglas({'bread' : 10, 'milk' : 1})
        self.produce(self.plastic_utility_function, {'bread' : 20, 'milk' : 1})

        """
        formula = 'utility =' + str(multiplier) + '*' + ('*'.join(['**'.join([input_good, str(input_quantity)]) for input_good, input_quantity in exponents.iteritems()]))
        self._utility_function = {}
        self._utility_function['type'] = 'cobb-douglas'
        self._utility_function['parameters'] = exponents
        self._utility_function['formula'] = compiler.compile(formula, '<string>', 'exec')
        self._utility_function['input'] = exponents.keys()

def predict_utility(utility_function, input_goods):
    """ Calculates the utility of a production (but does not consume)

        Predicts the utility of consume_with_utility(utility_function, input_goods)

    Args::

        utility_function: A utility_function produced with
        create_utility_function or create_cobb_douglas
        {'input_good1': amount1, 'input_good2': amount2 ...}: dictionary
        containing the amount of input good used for the production.

    Returns::

        utility: Number

    Example::

        print(A.predict_utility(self._utility_function, {'ball': 2, 'paint': 1}))


    """
    goods_vector = input_goods.copy()
    goods_vector['utility'] = None
    exec(utility_function['formula'], {}, goods_vector)
    return goods_vector['utility']

def sort(objects, key='price', reverse=False):
    """ Sorts the object by the key

    Args::

     reverse=True for descending

    Example::

        quotes_by_price = sort(quotes, 'price')
        """
    return sorted(objects, key=lambda objects: objects[key], reverse=reverse)


class Offer:
    """ container to send offers via zmq
    using self._send_class(receiver, '_o', offer)
    """
    def __init__(self, sender, receiver, good, quantity, price, buysell='s', idn=None):
        """ quotes have no idn """
        self.sender = sender
        self.receiver = receiver
        self.good = good
        self.quantity = quantity
        self.price = price
        self.buysell = buysell
        self.idn = idn

class NotEnoughGoods(Exception):
    """ Methods raise this exception when the agent has less goods than needed

    This functions (self.produce, self.offer, self.sell, self.buy)
    should be encapsulated by a try except block::

     try:
        self.produce(...)
     except NotEnoughGoods:
        alternative_statements()

    """
    def __init__(self, agent_name, good, amount_missing):
        self.good = good
        self.amount_missing = amount_missing
        self.name = agent_name
        Exception.__init__(self)
    def __str__(self):
        return repr(self.name + " '" + str(self.amount_missing) +" of good '" + self.good + "' missing")

class GoodDoesNotExist(KeyError):
    """ The good 'self.good' does not exist for this agent
    (usually a programming error) """
    def __init__(self, agent_name, good):
        KeyError.__init__(self)
        self.good = good
        self.name = agent_name
    def __str__(self):
        return repr(self.name + " '" + self.good + "' does not exist")
