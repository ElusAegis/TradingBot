#!/usr/bin/env python3

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk

import plots as plt
from simulator_logic import *


class LogicSettings:
    def __init__(self, setting_dict=None):
        self.settings = {
         "stock_name": "Carriage Service",
         "game_mode": GameMode.OFFLINE,
         "file_path": "stock_data/Carriage_Service.csv",
         "safe_mode": False
        }
        if setting_dict is not None:
            self.update(setting_dict)

    def update(self, setting_dict):
        for key in setting_dict.keys():
            self.settings[key] = setting_dict.get(key)


class StyleSettings:
    def __init__(self, bt_color="gray", txt_color="black"):
        self.bt_color = bt_color
        self.txt_color = txt_color


class TradingSimulator(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.iconphoto(self, tk.PhotoImage(file="app_data/appicon.icon"))
        self.title("Trading Simulator")
        self.logic_settings = LogicSettings()

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (MainMenu, PriceChart, PriceChartSettings):
            frame = F(container, self)

            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.center_window()
        self.show_frame(MainMenu)

    def show_frame(self, cont, restart=False):
        frame = self.frames[cont]
        if restart:
            frame.start()
        frame.tkraise()

    def center_window(self):
        self.update()
        w = self.winfo_width()
        h = self.winfo_height()

        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()

        x = (sw - w) / 2
        y = (sh - h) / 2
        self.geometry('%dx%d+%d+%d' % (w, h, x, y))

    def get_setting(self, setting):
        return self.logic_settings.settings.get(setting)


class MainMenu(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.controller = controller
        self.style = StyleSettings()

        self.init_ui()

    def init_ui(self):
        lbl = tk.Label(self, text="Main Menu")
        lbl.pack(side="top")
        # Set up buttons
        button1 = tk.Button(self, text="Live Price Chart",
                            command=lambda: self.controller.show_frame(PriceChartSettings),
                            bg = self.style.bt_color)
        button1.pack()


class PriceChartSettings(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.controller = controller
        self.style = StyleSettings()

        self.selected = tk.Variable()
        self.safe_mode = tk.BooleanVar()
        self.safe_mode.set(False)

        self.init_ui()

    def init_ui(self):

        lbl = tk.Label(self, text="Price Chart Settings")
        lbl.grid(column=3, columnspan=2, rowspan=2, pady=30)

        lbl_game_mode = tk.Label(self, text="Select game mode:")
        lbl_game_mode.grid(column=3, columnspan=2, row=3, pady=30)

        rad_online = tk.Radiobutton(self, text="Online", value=GameMode.ONLINE, variable=self.selected)
        rad_offline = tk.Radiobutton(self, text="Offline", value=GameMode.OFFLINE, variable=self.selected)
        rad_online.grid(columnspan=3, column=4, row=4)
        rad_offline.grid(columnspan=3, column=1, row=4)

        lbl_off_settings = tk.Label(self, text="Offline Settings:")
        lbl_off_settings.grid(columnspan=2, column=1, row=6, pady=30)

        lbl_file_loc = tk.Label(self, text="File location")
        lbl_file_loc.grid(columnspan=2, column=1, row=8, pady=10)
        self.__txt_file_loc = tk.Entry(self, width=20)
        self.__txt_file_loc.grid(columnspan=2, column=1, row=9)

        lbl_onl_settings = tk.Label(self, text="Online Settings:")
        lbl_onl_settings.grid(columnspan=2, column=5, row=6, pady=30)

        lbl_stock_name = tk.Label(self, text="Stock Name")
        lbl_stock_name.grid(columnspan=2, column=5, row=8, pady=10)
        self.__txt_stock_name = tk.Entry(self, width=10)
        self.__txt_stock_name.grid(columnspan=2, column=5, row=9)

        lbl_safe_mode = tk.Label(self, text="Safe Mode:")
        rad_safe = tk.Radiobutton(self, text="On", value=True, variable=self.safe_mode)
        rad_unsafe = tk.Radiobutton(self, text="Off", value=False, variable=self.safe_mode)
        lbl_safe_mode.grid(columnspan=2, column=5, row=10, pady=10)
        rad_safe.grid(columnspan=1, column=5, row=11)
        rad_unsafe.grid(columnspan=1, column=6, row=11)

        bt_save = tk.Button(self, text="Save settings",
                                command=self.save_data,
                                bg=self.style.bt_color)
        bt_save.grid(columnspan=2, column=3, row=12, pady=10)

        bt_pr_chart = tk.Button(self, text="Live Price Chart",
                            command=lambda: self.controller.show_frame(PriceChart, restart=True),
                            bg=self.style.bt_color)
        bt_pr_chart.grid(columnspan=2, column=3, row=13, pady=50)

        bt_main_menu = tk.Button(self, text="Back to Main Menu",
                            command=lambda: self.controller.show_frame(MainMenu),
                            bg=self.style.bt_color)
        bt_main_menu.grid(columnspan=2, column=3, row=14, pady=10)

    def save_data(self):
        new_settings = dict()

        new_path = self.__txt_file_loc.get()
        if new_path != "":
            new_settings["file_path"] = new_path
            new_settings["stock_name"] = new_path.rstrip(".csv").replace("_", " ")

        new_stock_name = self.__txt_stock_name.get()
        if new_stock_name != "":
            new_settings["stock_name"] = new_stock_name

        new_settings["safe_mode"] = self.safe_mode.get()
        new_settings["game_mode"] = GameMode.from_str(self.selected.get())

        self.controller.logic_settings.update(new_settings)


class PriceChart(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.controller = controller
        self.style = StyleSettings()

        self.timeout = 1000
        self.chart_size = tk.IntVar()
        self.chart_size.set(value=20)
        self.axes = None
        self.plot = None
        self.canvas = None

        self.lbl_score1 = None
        self.lbl_score2 = None

        self.game = GameLogic()

        self.init_ui()

    def init_ui(self):

        stock_name = self.controller.get_setting("stock_name")

        lbl = tk.Label(self, text="Price Chart")
        lbl.grid(columnspan=5, row=1)

        # Set up empty graph
        self.init_graph()


        # Set up entries
        lbl_player1 = tk.Label(self, text="Player 1:\n")
        lbl_buy1 = tk.Label(self, text="Amount to buy / sell:\n")
        txt_buy1 = tk.Entry(self, width=10)
        lbl_player1.grid(column=1, columnspan=2, row=2)
        lbl_buy1.grid(column=1, columnspan=2, row=3)
        txt_buy1.grid(column=1, columnspan=2, row=4)
        button_buy1 = tk.Button(self, text="Buy",
                                command=lambda: update(self.game.buy(1, float(txt_buy1.get()))))
        button_buy1.grid(column=1, row=5)
        button_sell1 = tk.Button(self, text="Sell",
                                command=lambda: update(self.game.sell(1, float(txt_buy1.get()))))
        button_sell1.grid(column=2, row=5)

        lbl_stock_amount1 = tk.Label(self, text="Stock amount: %.2f" % 0)
        lbl_money_amount1 = tk.Label(self, text="Money amount: %.2f" % 0)
        lbl_stock_amount1.grid(column=1, columnspan=2, row=7)
        lbl_money_amount1.grid(column=1, columnspan=2, row=8)

        # Set up entries
        lbl_player2 = tk.Label(self, text="Player 2:\n")
        lbl_buy2 = tk.Label(self, text="Enter amount to buy \ sell:\n")
        txt_buy2 = tk.Entry(self, text="Amount to buy:", width=10)
        lbl_player2.grid(column=4, columnspan=2, row=2)
        lbl_buy2.grid(column=4, columnspan=2, row=3)
        txt_buy2.grid(column=4, columnspan=2, row=4)
        button_buy2 = tk.Button(self, text="Buy",
                                command=lambda: update(self.game.buy(2, float(txt_buy1.get()))))
        button_buy2.grid(column=4, row=5)
        button_sell2 = tk.Button(self, text="Sell",
                                command=lambda: update(self.game.sell(2, float(txt_buy1.get()))))
        button_sell2.grid(column=5, row=5)

        lbl_stock_amount2 = tk.Label(self, text="Stock amount: %.2f" % 0)
        lbl_money_amount2 = tk.Label(self, text="Money amount: %.2f" % 0)
        lbl_stock_amount2.grid(column=4, columnspan=2, row=7)
        lbl_money_amount2.grid(column=4, columnspan=2, row=8)

        def update(*args, **kwargs):
            lbl_stock_amount1.config(text="Stock amount: %.2f" % self.game.player1.stock_volume,
                                     fg="black" if self.game.player1.stock_volume >= 0 else "red")

            lbl_stock_amount2.config(text="Stock amount: %.2f" % self.game.player2.stock_volume,
                                     fg="black" if self.game.player2.stock_volume >= 0 else "red")

            lbl_money_amount1.config(text="Money amount: %.2f" % self.game.player1.balance,
                                     fg="black" if self.game.player1.balance >= 0 else "red")

            lbl_money_amount2.config(text="Money amount: %.2f" % self.game.player2.balance,
                                     fg="black" if self.game.player2.balance >= 0 else "red")

        spin_size = tk.Spinbox(self, from_=0, to=100, textvariable=self.chart_size)
        spin_size.grid(column=3, columnspan=1, row=12)

        self.lbl_score1 = tk.Label(self, text="Player 1 score: %.3f" % 0)
        self.lbl_score2 = tk.Label(self, text="Player 2 score: %.3f" % 0)
        self.lbl_score1.grid(column=1, columnspan=2, row=13)
        self.lbl_score2.grid(column=4, columnspan=2, row=13)

        # Set up buttons
        button1 = tk.Button(self, text="Settings",
                            command=lambda: self.controller.show_frame(PriceChartSettings),
                            bg=self.style.bt_color)
        button1.grid(column=3, row=14)

        button2 = tk.Button(self, text="Back to Main Menu",
                            command=lambda: self.controller.show_frame(MainMenu),
                            bg=self.style.bt_color)
        button2.grid(column=3, row=15)

    def init_graph(self):
        self.plot, self.axes = plt.init_plot(self.controller.get_setting("stock_name"))
        self.canvas = FigureCanvasTkAgg(self.plot, self)
        self.canvas.get_tk_widget().grid(column=3, rowspan=12, row=2)

    def update(self):
        data = self.game.update_data(self.chart_size.get())

        plt.draw_plot(self.plot, self.axes, data, self.chart_size.get())
        self.canvas.draw()

        scores = self.game.scores()
        self.lbl_score1.config(text="Player 1 score: %.3f" % scores[0],
                                     fg="black" if scores[0] >= 0 else "red")
        self.lbl_score2.config(text="Player 2 score: %.3f" % scores[1],
                                     fg="black" if scores[1] >= 0 else "red")

        self.parent.after(self.timeout, self.update)

    def start(self):
        self.game = GameLogic(stock_name=self.controller.get_setting("stock_name"),
                              game_mode=self.controller.get_setting("game_mode"),
                              file_path=self.controller.get_setting("file_path"),
                              safe=self.controller.get_setting("safe_mode"))
        self.controller.after(self.timeout, self.update)


def main():
    app = TradingSimulator()
    app.mainloop()


if __name__ == "__main__":
    main()
