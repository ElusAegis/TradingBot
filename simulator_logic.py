import enum
import pandas as pd
import random

from APIinteraction import *
from dummy_bot import *


class GameMode(enum.Enum):
    ONLINE = 1
    OFFLINE = 2

    @staticmethod
    def from_str(game_mode_str):
        if game_mode_str == "ONLINE" or game_mode_str == "GameMode.ONLINE":
            return GameMode.ONLINE
        if game_mode_str == "OFFLINE" or game_mode_str == "GameMode.OFFLINE":
            return GameMode.OFFLINE


class Player:
    def __init__(self, alive):
        self.balance = 0
        self.stock_volume = 0

        if not alive:
            self.decision_maker = DummyBot()

    def buy(self, amount, price):
        self.balance -= amount * price
        self.stock_volume += amount

    def sell(self, amount, price):
        # if self.stock_volume < amount:
        #     raise ValueError("Not enough stocks to sell {}!".format(amount))
        self.balance += amount * price
        self.stock_volume -= amount


class OnlineGame:

    def __init__(self, stock_name="ETHBTC", safe=False):
        self.stock_name = stock_name
        try:
            self.bnAPI = BinanceApi(safe=safe)
        except ConnectionError or ConnectionRefusedError:
            raise ConnectionError("Unable to initialise online game, going offline!")

        if self.bnAPI.safe and not (list(filter(lambda x: x["symbol"] == stock_name, self.bnAPI.exchange_info["symbols"]))):
            raise ValueError("Invalid stock name {}!".format(stock_name))

    def get_new_price(self):
        return float(self.bnAPI.get_cur_price(self.stock_name))


class OfflineGame:
    def __init__(self, file_path="stock_data/Carriage_Service.csv"):
        try:
            self.data_frame = pd.read_csv(file_path)
        except FileNotFoundError:
            raise FileNotFoundError("The {} file was not found!".format(file_path))
        self.df_index = int(random.random() * self.data_frame.shape[0] / 3 * 2)

    def get_new_price(self):
        if self.df_index >= self.data_frame.shape[0]:
            self.df_index = int(random.random * self.data_frame.shape[0] / 3 * 2)
            raise Warning("Resetting the data for chart")
        self.df_index += 1
        return float(self.data_frame["Close"][self.df_index])


class GameLogic:
    def __init__(self, player1=True, player2=True, game_mode=GameMode.OFFLINE, stock_name="ETHBTC", file_path="stock_data/Carriage_Service.csv",
                 safe=False):

        self.player1 = Player(player1)
        self.player2 = Player(player2)

        self.game_mode = game_mode
        self.data = {"price": [], "name": stock_name}

        if game_mode is GameMode.ONLINE:
            try:
                self.game_engine = OnlineGame(stock_name=stock_name, safe=safe)
            except ConnectionError:
                self.game_engine = OfflineGame(file_path)

        if game_mode is GameMode.OFFLINE:
            self.game_engine = OfflineGame(file_path)

    def update_data(self, size):

        price = self.game_engine.get_new_price()
        self.data["price"].append(price)
        show_data = {
            "price": self.data["price"][-size: -1],
            "name": self.data["name"]}
        return show_data

    def scores(self):
        if len(self.data["price"]) == 0:
            return [0, 0]
        return [self.data["price"][-1] * self.player1.stock_volume + self.player1.balance,
                self.data["price"][-1] * self.player2.stock_volume + self.player2.balance]

    def sell(self, index, amount):
        price = self.data["price"][-1]
        if index == 1:
            self.player1.sell(amount, price)
        if index == 2:
            self.player2.sell(amount, price)

    def buy(self, index, amount):
        price = self.data["price"][-1]
        if index == 1:
            self.player1.buy(amount, price)
        if index == 2:
            self.player2.buy(amount, price)

    def question(self, index):
        price = self.data["price"][-1]
        if index == 1:
            amount = self.player1.decision_maker.buy(price)
            if not amount:
                amount = self.player1.decision_maker.sell(price)
                self.player1.sell(amount, price)
            else:
                self.player1.buy(amount, price)

        if index == 2:
            amount = self.player2.decision_maker.buy(price)
            if not amount:
                amount = self.player2.decision_maker.sell(price)
                self.player2.sell(amount, price)
            else:
                self.player2.buy(amount, price)
