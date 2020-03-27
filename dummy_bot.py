""" This is a very naive bot that buy when it has no open orders and sells
 if the price went up, of if the time limit for an order is exceeded.
 It can only hold one order at a time
"""

import time


class DummyBot:
    def __init__(self, max_hold=50, buy_amount=40):
        self.__open_order = False
        self.buy_price = None
        self.timer = 0
        self.max_hold = max_hold
        self.buy_amount = buy_amount

    def buy(self, price):
        self.timer += 1

        if not self.__open_order:
            self.buy_price = price
            self.__open_order = True
            self.timer = 0
            return self.buy_amount
        return 0

    def sell(self, price):
        self.timer += 1

        if self.buy_price < price or self.max_hold < self.timer:
            self.__open_order = False
            return self.buy_amount
        return 0
