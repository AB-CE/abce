#pylint: disable=C0111, E1103, E1101
import pandas as pd
import pygal as pg

def generate():

    columns = ['total_orders', 'cookies_created', 'cookies_inventory', 'price_price', 'production_production']

    firm = pd.read_csv('firm.csv')

    firm = firm.fillna(method='ffill')
    firm = firm.fillna(method='bfill')

    graph = pg.Line(width=800, height=400, explicit_size=True, dots_size=1)
    for column in columns:
        graph.add(column, firm[column])
    graph.render_in_browser()
