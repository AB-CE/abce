"""
functions:
sam_cell(seller, buyer, cell='quantity'), returns you the evolution over time of a cell
trade_over_time(seller, buyer, good, cell='quantity'), returns you the evolution over time of a cell
sam(t), returns the social accounting matrix at time t
sam_ext(t), returns the social accounting matrix at time t for every individual agent
"""
import os
import sqlite3
import pandas as pd


def to_csv(directory):
    os.chdir(directory)
    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    for table_name in tables:
        table_name = table_name[0]
        table = pd.read_sql_query("SELECT * from %s" % table_name, db)
        table.to_csv(table_name + '.csv')
        if u'id' in table.columns:
            del table['id']
            grouped = table.groupby('round')
            aggregated = grouped.sum()
            aggregated.to_csv(table_name + '_aggregate.csv')
            try:
                meaned = grouped.mean()
                meaned.to_csv(table_name + '_mean.csv')
            except pd.core.groupby.DataError:
                pass




