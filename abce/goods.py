from .inventory import Inventory


class Goods:
    """ Each agent can access his goods. self['good_name'] shows the quantity of goods of a certain type an agent
    owns. Goods can be a string or any other python object.
    """
    def __init__(self, id, agent_parameters, simulation_parameters, group, trade_logging,
                 database, check_unchecked_msgs, expiring, perishable, resource_endowment, start_round=None):
        self._inventory = Inventory((group, id))
        self._resources = []

    def possession(self, good):
        """ returns how much of good an agent possesses.

        Returns:
            A number.

        possession does not return a dictionary for self.log(...), you can use
        self.possessions([...]) (plural) with self.log.

        Example::

            if self['money'] < 1:
                self.financial_crisis = True

            if not(is_positive(self['money']):
                self.bancrupcy = True

        """
        print("depreciated use self[good] or self.not_reserved[good]")
        return self._inventory[good]

    def possessions(self):
        """ returns all possessions """
        return self._inventory.possessions()

    def create(self, good, quantity):
        """ creates quantity of the good out of nothing

        Use create with care, as long as you use it only for labor and
        natural resources your model is macro-economically complete.

        Args:
            'good': is the name of the good
            quantity: number
        """
        self._inventory.create(good, quantity)

    def create_timestructured(self, good, quantity):
        """ creates quantity of the time structured good out of nothing.
        For example::

            self.creat_timestructured('capital', [10,20,30])

        Creates capital. 10 units are 2 years old 20 units are 1 year old
        and 30 units are new.

        It can alse be used with a quantity instead of an array. In this
        case the amount is equally split on the years.::

            self.create_timestructured('capital', 60)

        In this case 20 units are 2 years old 20 units are 1 year old
        and 20 units are new.

        Args:
            'good':
                is the name of the good

            quantity:
                an arry or number
        """
        self._inventory.create_timestructured(good, quantity)

    def _declare_expiring(self, good, duration):
        """ creates a good that has a limited duration
        """
        self._inventory._declare_expiring(good, duration)

    def not_reserved(self, good):
        """ Returns the amount of goods that are not reserved for a trade

        Args:
            good
        """
        return self._inventory.not_reserved(good)

    def destroy(self, good, quantity=None):
        """ destroys quantity of the good. If quantity is omitted destroys all

        Args::

            'good':
                is the name of the good
            quantity (optional):
                number

        Raises::

            NotEnoughGoods: when goods are insufficient
        """
        self._inventory.destroy(good, quantity)

    def _register_resource(self, resource, units, product):
        self._resources.append((resource, units, product))

    def _register_perish(self, good):
        self._inventory._perishable.append(good)

    def __getitem__(self, good):
        return self._inventory.haves[good]
