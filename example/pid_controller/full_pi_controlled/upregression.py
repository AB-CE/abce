from builtins import object
#pylint: disable=C0103, W0201
from sklearn import linear_model


class UPRegression(object):
    def __init__(self, memory):
        self.memory = memory
        self.learn_delta_price = linear_model.LinearRegression()
        self.learn_price = linear_model.LinearRegression()
        self.dX = []
        self.dy = []
        self.X = []
        self.y = []


    def fit(self, price, price_1, L, L_1):
        self.price = price
        self.price_1 = price_1
        self.L = L
        self.L_1 = L_1
        self.y.append(price)
        self.dy.append(price - price_1)
        self.dX.append([1, L - L_1, price_1, L_1])
        self.X.append([1, L])
        if len(self.y) >= self.memory:
            del self.y[0]
            del self.dy[0]
            del self.X[0]
            del self.dX[0]

        self.learn_delta_price.fit(self.dX, self.dy)
        self.learn_price.fit(self.X, self.y)

    def predict(self):
        B_p = self.learn_delta_price.coef_
        error_delta_price = self.learn_delta_price.predict([1, self.L - self.L_1, self.price_1, self.L_1]) + self.price_1  - self.price
        error_price = self.learn_price.predict([1, self.L]) - self.price
        self.up_delta_price = - B_p[3] / B_p[2] * self.L
        self.up_price = self.learn_price.coef_[1] * self.L
        if error_delta_price ** 2 < error_price ** 2:
            up = self.up_delta_price
        else:
            up = self.up_price
        return up
