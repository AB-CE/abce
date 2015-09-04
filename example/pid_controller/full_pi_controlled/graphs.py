#pylint: disable=C0111, E1103, E1101
import pandas as pd
import pygal as pg

def generate():
    firm = pd.read_csv('firm.csv')

    columns = ['total_orders', 'production_cookies', 'price_price', 'production_production']

    firm = firm.fillna(method='ffill')
    firm = firm.fillna(method='bfill')

    graph = pg.Line(width=800, height=400, explicit_size=True, dots_size=1)
    for column in columns:
        graph.add(column, firm[column])

    graph.add('cookies_inventory', firm['cookies_inventory'], secondary=True)
    graph.render_in_browser()
