from abce.trade import get_epsilon
from collections import defaultdict
from abce.notenoughgoods import NotEnoughGoods
from copy import copy


epsilon = get_epsilon()


class Inventory(defaultdict):
    def __init__(self, name):
        super(Inventory, self).__init__(float)
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
        self[good] += quantity

    def create_timestructured(self, good, quantity):
        """ creates quantity of the time structured good out of nothing.
        For example::

            self.creat_timestructured('capital', [10,20,30])

        Creates capital. 10 units are 2 years old 20 units are 1 year old
        and 30 units are new.

        It can alse be used with a quantity instead of an array. In this
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
        length = len(self[good].time_structure)
        for i in range(length):
            qty = quantity[i] if type(quantity) == list else quantity / length
            self[good].time_structure[i] += qty

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
            self[good] = 0
        else:
            assert quantity >= 0.0
            available = self[good]
            if available < quantity - epsilon:
                raise NotEnoughGoods(self.name, good, quantity - available)
            self[good] -= quantity

    def transform(self, ingredient, unit, product, quantity=None):
        if quantity is None:
            quantity = self[ingredient]
        self.destroy(ingredient, quantity)
        self.create(product, float(unit) * quantity)

    def possession(self, good):
        """ returns how much of good an agent possesses.

        Returns:
            A number.

        possession does not return a dictionary for self.log(...), you can use self.possessions([...])
        (plural) with self.log.

        Example::

            if self.possession('money') < 1:
                self.financial_crisis = True

            if not(is_positive(self.possession('money')):
                self.bankruptcy = True

        """
        return float(self[good])

    def possessions(self):
        """ returns all possessions """
        return copy(super())

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
            self[good]._advance_round()

        # perishing goods
        for good in self._perishable:
            if good in self:
                self.destroy(good)
