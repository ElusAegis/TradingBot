import matplotlib
from matplotlib.figure import Figure
matplotlib.use("TkAgg")


def init_plot(name):

    f = Figure(figsize=(5, 5), dpi=100)

    ax = f.add_subplot(111)

    return f, ax


def draw_plot(f, ax, data, x_size):

    f.suptitle("Life price for %s" % data["name"])

    y_min_size = 0
    y_max_size = 1
    if data["price"]:
        calibration = max(data["price"]) / min(data["price"])
        y_max_size = max(data["price"]) * 1.00001 * calibration
        y_min_size = min(data["price"]) * 0.99999 / calibration

    ax.clear()
    ax.plot(list(range(0, len(data["price"]))), data["price"], color='black')
    ax.axis([0, x_size, y_min_size, y_max_size])

    ax.set_ylabel('price: ' + data["name"])
    ax.set_xlabel('t')

    # Turn off tick labels
    ax.set_xticklabels([])


def main():
    data = {"x": [0,1,2,3,4,5], "y": [0,1,4,9,16,25], "name": "name"}

if __name__ == "__main__":
    main()