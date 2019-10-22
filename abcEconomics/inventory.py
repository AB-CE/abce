from abcEconomics.agents.trader import get_epsilon
from collections import defaultdict
from abcEconomics.notenoughgoods import NotEnoughGoods
from .expiringgood import ExpiringGood

epsilon = get_epsilon()


def isclose(a, b):
    rel_tol = 1e-9
    return abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), 0.0)


class Inventory(object):
    def __init__(self, name):
        self.haves = defaultdict(int)
        self._reserved = defaultdict(int)
        self.name = name
        self._expiring_goods = []
        self._perishable = []

    def create(self, good, quantity):
        """ creates quantity of the good out of nothing

        Use with care. As long as you use it only for labor and
        natural resources your model is macro-economically complete.

        Args:
            'good': is the name of the good
            quantity: number
        """
        assert quantity >= 0.0
        self.haves[good] += quantity

    def create_timestructured(self, good, quantity):
        """ creates quantity of the time structured good out of nothing.
        For example::

            self.creat_timestructured('capital', [10,20,30])

        Creates capital. 10 units are 2 years old 20 units are 1 year old
        and 30 units are new.

        It can also be used with a quantity instead of an array. In this
        case the amount is equally split on the years.::

            self.creat_timestructured('capital', 60)

        In this case 20 units are 2 years old 20 units are 1 year old
        and 20 units are new.

        Args:
            'good':
                is the name of the good

            quantity:
                an arry or number
        """
        length = len(self.haves[good].time_structure)
        for i in range(length):
            qty = quantity[i] if type(quantity) == list else quantity / length
            self.haves[good].time_structure[i] += qty

    def destroy(self, good, quantity=None):
        """ destroys quantity of the good. If quantity is omitted destroys all

        Use with care.

        Args::

            'good':
                is the name of the good
            quantity (optional):
                number

        Raises::

            NotEnoughGoods: when goods are insufficient
        """
        if quantity is None:
            self.haves[good] = 0
        else:
            assert quantity >= 0.0
            available = self.haves[good]
            if available < quantity - epsilon:
                raise NotEnoughGoods(self.name, good, quantity - available)
            self.haves[good] -= quantity

    def reserve(self, good, quantity):
        self._reserved[good] += quantity
        if self._reserved[good] > self.haves[good]:
            if isclose(self._reserved[good], self.haves[good]):
                self._reserved[good] = self.haves[good]
            else:
                self._reserved[good] -= quantity
                raise NotEnoughGoods(self.name, good, quantity - (self.haves[good] - self._reserved[good]))

    def rewind(self, good, quantity):
        self._reserved[good] -= quantity

    def commit(self, good, committed_quantity, final_quantity):
        self._reserved[good] -= committed_quantity
        self.haves[good] -= final_quantity

    def transform(self, ingredient, unit, product, quantity=None):
        if quantity is None:
            quantity = self.haves[ingredient]
        self.destroy(ingredient, quantity)
        self.create(product, float(unit) * quantity)

    def possession(self, good):
        return self.not_reserved(good)

    def not_reserved(self, good):
        """ returns how much of good an agent possesses.

        Returns:
            A number.

        possession does not return a dictionary for self.log(...), you can use self.possessions([...])
        (plural) with self.log.

        Example::

            if self['money'] < 1:
                self.financial_crisis = True

            if not(is_positive(self['money']):
                self.bankruptcy = True

        """
        return float(self.haves[good] - self._reserved[good])

    def reserved(self, good):
        """ returns how much of a good an agent has currently reseed to sell or buy.

        Returns:
            A number.

        possession does not return a dictionary for self.log(...), you can use self.possessions([...])
        (plural) with self.log.

        Example::

            if self['money'] < 1:
                self.financial_crisis = True

            if not(is_positive(self['money']):
                self.bankruptcy = True

        """
        return self._reserved[good]

    def possessions(self):
        """ returns all possessions """
        return {good: float(self.haves[good] - self._reserved[good]) for good in self.haves}

    def calculate_netvalue(self, prices):
        return sum(quantity * prices[name]
                   for name, quantity in self.items())

    def calculate_assetvalue(self, prices):
        return sum(quantity * prices[name]
                   for name, quantity in self.items()
                   if prices[name] > 0)

    def calculate_liablityvalue(self, prices):
        return sum(quantity * prices[name]
                   for name, quantity in self.items()
                   if prices[name] < 0)

    def calculate_valued_assets(self, prices):
        ret = {name: quantity
               for name, quantity in self.items()
               if prices[name] >= 0}
        return ret

    def calculate_valued_liablities(self, prices):
        ret = {name: quantity
               for name, quantity in self.items()
               if prices[name] < 0}
        return ret

    def _advance_round(self):
        # expiring goods
        for good in self._expiring_goods:
            self.haves[good]._advance_round()

        # perishing goods
        for good in self._perishable:
            if good in self.haves:
                self.destroy(good)

    def __getitem__(self, good):
        return self.haves[good]

    def _declare_expiring(self, good, duration):
        self.haves[good] = ExpiringGood(duration)
        self._expiring_goods.append(good)
