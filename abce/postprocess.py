"""
functions:
sam_cell(seller, buyer, cell='quantity'), returns you the evolution over time of a cell
trade_over_time(seller, buyer, good, cell='quantity'), returns you the evolution over time of a cell
sam(t), returns the social accounting matrix at time t
sam_ext(t), returns the social accounting matrix at time t for every individual agent
"""
import os
import numpy
import dataset
import csv
import pandas as pd



@profile
def to_csv(directory, db_name): #pylint: disable=R0914
    os.chdir(directory)
    #db_name = db_name + '.db'
    db = dataset.connect('sqlite:///database.db')

    # dumps csv file
    for table_name in db.tables:
        with open(table_name + '.csv', 'w') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(db[table_name].columns)
            for row in db[table_name]:
                writer.writerow(row.values())

    for table_name in db.tables:
        table = pd.read_csv(table_name + '.csv')
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




