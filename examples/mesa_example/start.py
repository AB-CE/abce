""" This is a simple demonstration model how to integrate abcEconomics and mesa.
The model and scheduler specification are taken care of in
abcEconomics instead of Mesa.

Based on
https://github.com/projectmesa/mesa/tree/master/examples/boltzmann_wealth_model.

For further reading, see
[Dragulescu, A and Yakovenko, V. Statistical Mechanics of Money, Income, and Wealth: A Short Survey. November, 2002](http://arxiv.org/pdf/cond-mat/0211175v1.pdf)
"""
from model import MoneyModel
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import ChartModule


def agent_portrayal(agent):
    """ This function returns a big red circle, when an agent is wealthy and a
    small gray circle when he is not """
    portrayal = {"Shape": "circle",
                 "Filled": "true",
                 "r": 0.5}

    if agent.report_wealth() > 0:
        portrayal["Color"] = "red"
        portrayal["Layer"] = 0
    else:
        portrayal["Color"] = "grey"
        portrayal["Layer"] = 1
        portrayal["r"] = 0.2
    return portrayal


def main(x_size, y_size):
    """ This function sets up a canvas to graphically represent the model 'MoneyModel'
    and a chart, than it runs the server and runs the model in model.py in the browser """
    grid = CanvasGrid(agent_portrayal, x_size, y_size, 500, 500)

    chart = ChartModule([{"Label": "Gini",
                          "Color": "Black"}],
                        data_collector_name='datacollector')
    # the simulation uses a class DataCollector, that collects the data and
    # relays it from self.datacollector to the webpage

    server = ModularServer(MoneyModel,
                           [grid, chart],
                           "abcEconomics and MESA integrated",
                           x_size * y_size, x_size, y_size)
    server.port = 8534  # change this number if address is in use
    server.launch()


if __name__ == '__main__':
    main(25, 25)
