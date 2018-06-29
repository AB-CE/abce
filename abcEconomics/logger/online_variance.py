class OnlineVariance:
    def __init__(self):
        self.clear()

    def clear(self):
        self.n = 0
        self.M2 = 0.0
        self._mean = 0.0

    def update(self, x):
        self.n += 1
        delta = x - self._mean
        self._mean += delta / self.n
        delta2 = x - self._mean
        self.M2 += delta * delta2

    def std(self):
        if self.n < 2:
            return 0.0
        else:
            return (self.M2 / (self.n - 1)) ** 0.5

    def mean(self):
        return self._mean

    def sum(self):
        return self._mean * self.n
