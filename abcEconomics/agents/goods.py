from ..inventory import Inventory
from ..notenoughgoods import NotEnoughGoods


class Goods:
    """ Each agent can access his goods. self['good_name'] shows the quantity of goods of a certain type an agent
    owns. Goods can be a string or any other python object.
    """

    def __init__(self, id, agent_parameters, simulation_parameters):
        # unpack simulation_parameters
        group = simulation_parameters['group']

        self._inventory = Inventory((group, id))
        self._resources = []

    def refresh_services(self, service, derived_from, units=1):
        self.destroy(service)
        self.create(service, getattr(self, derived_from) * units)

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

    def transform(self, inputs, outputs):
        """ Transforms a dictionary of goods into a new dictionary of goods.
        Raises NotEnoughGoods exception if not enough input goods are available

        Args:
            inputs: dictionary of goods and quantities, that are used in the transformation
            outputs: dictionary of goods and quantities, that are created by the transformation

        Example::

            self.transform(inputs={'gold': 1, 'copper': 4}, outputs={'redgold': 5})
        """
        for good, quantity in inputs.items():
            if self._inventory.haves[good] < quantity:
                raise NotEnoughGoods(self.name, good, quantity - self._inventory.haves[good])
        for good, quantity in inputs.items():
            self._inventory.destroy(good, quantity)
        for good, quantity in outputs.items():
            self._inventory.create(good, quantity)

    def __getitem__(self, good):
        return self._inventory.haves[good]
