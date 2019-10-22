from collections import deque
from abcEconomics.notenoughgoods import NotEnoughGoods
from abcEconomics.agents.trader import get_epsilon
epsilon = get_epsilon()


class ExpiringGood(object):
    """ A good that expires after X rounds """

    def __init__(self, duration):
        self.duration = duration
        self.time_structure = deque([0 for _ in range(duration)])  # old to new

    def _advance_round(self):
        del self.time_structure[0]
        self.time_structure.append(0)

    def __add__(self, other):
        if isinstance(other, ExpiringGood):
            self.time_structure = [
                s + o for s, o in zip(self.time_structure, other.time_structure)]
        else:
            self.time_structure[-1] += other
        return self

    def __radd__(self, other):
        return other + sum(self.time_structure)

    def __sub__(self, other):
        if isinstance(other, ExpiringGood):
            other = float(other)
        if sum(self.time_structure) < - epsilon:
            raise NotEnoughGoods
        for i in range(len(self.time_structure)):
            if other >= self.time_structure[i]:
                other -= self.time_structure[i]
                self.time_structure[i] = 0
            else:
                self.time_structure[i] -= other
                break
        return self

    def __rsub__(self, other):
        return other - sum(self.time_structure)

    def __mul__(self, other):
        return sum(self.time_structure) * other

    def __floordiv__(self, other):
        return sum(self.time_structure) // other

    def __div__(self, other):
        return sum(self.time_structure) / other

    def __mod__(self, other):
        return sum(self.time_structure) % other

    def __pow__(self, other):
        return sum(self.time_structure) ** other

    def __cmp__(self, other):
        a = sum(self.time_structure)
        return (a > other) - (a < other)

    def __int__(self):
        return int(sum(self.time_structure))

    def __long__(self):
        return int(sum(self.time_structure))

    def __float__(self):
        return float(sum(self.time_structure))

    def __repr__(self):
        return str(sum(self.time_structure))

    def __get__(self, instance, owner=None):
        return sum(self.time_structure)

    def __abs__(self):
        return abs(self.__float__())
