import random
import pylab
from abce import Agent


def get_distance(pos_1, pos_2):
    x1, y1 = pos_1
    x2, y2 = pos_2
    dx = x1 - x2
    dy = y1 - y2
    return pylab.sqrt(dx ** 2 + dy ** 2)


class Sugar(Agent):
    def __init__(self, pos, max_sugar):
        self.pos = pos
        self.amount = max_sugar
        self.max_sugar = max_sugar

    def step(self):
        self.amount = min([self.max_sugar, self.amount + 1])


class Spice(Agent):
    def __init__(self, pos, max_spice):
        self.pos = pos
        self.amount = max_spice
        self.max_spice = max_spice

    def step(self):
        self.amount = min([self.max_spice, self.amount + 1])


class SsAgent(Agent):
    def init(self, parameters, agent_parameters):
        self.moore = False
        self.grid = parameters["grid"]
        self.set_at_random_unoccupied_pos()
        self.grid.place_agent(self, self.pos)
        self.sugar = random.randrange(25, 50)
        self.spice = random.randrange(25, 50)
        self.metabolism = random.randrange(1, 5)
        self.metabolism_spice = random.randrange(1, 5)
        self.vision = random.randrange(1, 6)
        self.prices = []

    def set_at_random_unoccupied_pos(self):
        x = random.randrange(self.grid.width)
        y = random.randrange(self.grid.height)
        if not self.is_occupied((x, y)):
            self.pos = (x, y)
            return
        self.set_at_random_unoccupied_pos()

    def get_sugar(self, pos):
        this_cell = self.grid.get_cell_list_contents([pos])
        for agent in this_cell:
            if type(agent) is Sugar:
                return agent

    def get_spice(self, pos):
        this_cell = self.grid.get_cell_list_contents([pos])
        for agent in this_cell:
            if type(agent) is Spice:
                return agent

    def get_ssagent(self, pos):
        this_cell = self.grid.get_cell_list_contents([pos])
        for agent in this_cell:
            if isinstance(agent, SsAgent):
                return agent

    def is_occupied(self, pos):
        this_cell = self.grid.get_cell_list_contents([pos])
        return len(this_cell) > 2

    def move(self):
        # hack this checkalive shouldn't be here
        if not self.check_alive():
            return
        # Epstein rule M
        # Get neighborhood within vision
        neighbors = [i for i in self.grid.get_neighborhood(self.pos, self.moore,
                     False, radius=self.vision) if not self.is_occupied(i)]
        neighbors.append(self.pos)
        eps = 0.0000001
        # Find the patch which produces maximum welfare
        welfares = [self.welfare(self.sugar + self.get_sugar(pos).amount,
                    self.spice + self.get_spice(pos).amount) for pos in neighbors]
        max_welfare = max(welfares)
        candidate_indices = [i for i in range(len(welfares)) if abs(welfares[i] -
                             max_welfare) < eps]
        candidates = [neighbors[i] for i in candidate_indices]
        # Find the nearest patch among the candidate
        try:
            min_dist = min([get_distance(self.pos, pos) for pos in candidates])
        except:
            print(welfares)
            print(self.welfare())
            print(self.sugar)
            print(self.spice)
            print(neighbors)
            exit()
        final_candidates = [pos for pos in candidates if abs(get_distance(self.pos,
                            pos) - min_dist) < eps]
        random.shuffle(final_candidates)
        self.grid.move_agent(self, final_candidates[0])

    def eat(self):
        if not self.check_alive():
            return
        sugar_patch = self.get_sugar(self.pos)
        spice_patch = self.get_spice(self.pos)
        self.sugar = self.sugar - self.metabolism + sugar_patch.amount
        self.spice = self.spice - self.metabolism_spice + spice_patch.amount
        sugar_patch.amount = 0
        spice_patch.amount = 0
        self.check_alive()

    def check_alive(self):
        # Starved to death
        if not self:
            return False
        if self.sugar <= 0 or self.spice <= 0:
            try:
                self.grid._remove_agent(self.pos, self)
                self.delete_agent('SsAgent', self.id)
            except:  # already died
                pass
            return False
        return True

    def sell_spice(self, other, price):
        if price >= 1:
            self.sugar += 1
            other.sugar -= 1
            self.spice -= int(price)
            other.spice += int(price)
        else:
            self.sugar += int(1 / price)
            other.sugar -= int(1 / price)
            self.spice -= 1
            other.spice += 1

    def revert_sell_spice(self, other, price):
        if price >= 1:
            self.sugar += 1
            other.sugar -= 1
            self.spice -= price
            other.spice += price
        else:
            self.sugar += 1 / price
            other.sugar -= 1 / price
            self.spice -= 1
            other.spice += 1

    def trade(self, other):
        # Epstein rule T for a pair of agents, page 105
        mrs_self = self.calculate_MRS()
        welfare_self = self.welfare()
        welfare_other = other.welfare()
        mrs_other = other.calculate_MRS()
        if mrs_self == mrs_other:
            return
        if self.sugar < 0 or self.spice < 0 or other.sugar < 0 or other.spice < 0:
            return
        if mrs_self < 0.01 or mrs_other < 0.01:
            return
        price = pylab.sqrt(mrs_self * mrs_other)
        self.prices.append(price)
        if mrs_self > mrs_other:
            # self is a sugar buyer
            self.sell_spice(other, price)
            if (welfare_self < self.welfare() or  # self is worse off
               welfare_other < other.welfare() or  # other is worse off
               self.calculate_MRS() < other.calculate_MRS()):  # self's MRS cross over other
                self.revert_sell_spice(other, price)
                return
        else:
            # self is a spice buyer
            other.sell_spice(self, price)
            if (welfare_self < self.welfare() or
               welfare_other < other.welfare() or
               self.calculate_MRS() > other.calculate_MRS()):
                other.revert_sell_spice(self, price)
                return
        # continue trading
        self.trade(other)

    def trade_with_neighbors(self):
        if not self.check_alive():
            return
        # von Neumann neighbors
        neighbor_agents = [self.get_ssagent(pos) for pos in self.grid.get_neighborhood(self.pos, self.moore,
                           False, radius=self.vision) if self.is_occupied(pos)]
        if neighbor_agents:
            random.shuffle(neighbor_agents)
            count = 0
            for a in neighbor_agents:
                if a:
                    self.trade(a)
                    count += 1
            if count > 0:
                prices = [p for p in self.prices if p]
                self.prices = []
                #print("%d Traded with %d out of %d neighbors" % (self.id, count, len(neighbor_agents)))
                return prices
        return []

    def welfare(self, sugar=None, spice=None):
        if sugar is None:
            sugar = self.sugar
        if spice is None:
            spice = self.spice
        m_total = self.metabolism + self.metabolism_spice
        return sugar ** (self.metabolism / m_total) * spice ** (self.metabolism_spice / m_total)

    def calculate_MRS(self):
        return (self.spice / self.metabolism_spice) / (self.sugar / self.metabolism)

    def compare_MRS(self, agent):
        return self.calculate_MRS() == agent.calculate_MRS()
