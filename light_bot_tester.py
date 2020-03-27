import pandas as pd
import random


class LightTester:

    def __init__(self, file_path="stock_data/Carriage_Service.csv", price_column="Close"):
        try:
            self.data_frame = pd.read_csv(file_path)[price_column]
        except FileNotFoundError:
            raise FileNotFoundError("The {} file was not found!".format(file_path))
        self.df_index = int(random.random() * self.data_frame.shape[0] / 3)
        self.money = 0
        self.round = 0
        self.stock = 0
        self.trade_count = 0

    def run(self, bot):

        def get_price():
            price = self.data_frame[self.df_index]
            return price

        def question(price):
            amount = bot.buy(price)
            if not amount:
                amount = bot.sell(price)
                self.stock -= amount
                self.money += amount * price
            else:
                self.stock += amount
                self.money -= amount * price

            if amount:
                self.trade_count += 1

        while self.df_index < self.data_frame.shape[0]:
            price = get_price()
            question(price)
            if not self.round % 1000:
                print("The bots current score is {:.2f} on {:.1f}% of the dataset".format(
                    self.money + self.stock * get_price(), self.df_index * 100. / self.data_frame.shape[0]
                ))
            self.df_index += 1

        print("Overall statistics: conducted %d trades, average profit %.3f"
              % (self.trade_count, (self.money + self.stock * price) / self.trade_count))


if __name__ == "__main__":
    import dummy_bot
    light_tester = LightTester(file_path="stock_data/crypto_currency/BNBBTC-5m-2017-01-01 00:00:00-data.csv",
                               price_column="close")
    light_tester.run(dummy_bot.DummyBot())
