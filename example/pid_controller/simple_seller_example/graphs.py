#pylint: disable=C0111, E1103, E1101
import pandas as pd
import pygal as pg

def generate():
    firm = pd.read_csv('firm.csv')

    firm = firm.fillna(method='ffill')
    firm = firm.fillna(method='bfill')

    graph = pg.Line(width=800, height=400, explicit_size=True, dots_size=1)
    graph.add('price', firm['_price'])
    graph.render_in_browser()

    household = pd.read_csv('panel_household.csv')

    household = household.fillna(method='ffill')
    household = household.fillna(method='bfill')

    graph = pg.Dot(width=800, height=400, explicit_size=True, dots_size=1)
    for i in range(10):
        graph.add('Household: %i cookies' % i, household[household['id'] == i]['cookies'])
    graph.render_in_browser()
