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


trade_unified = []  # placeholder value, since trade_unified seems to not have been defined in anywhere else


def to_csv(directory, db_name): #pylint: disable=R0914
    os.chdir(directory)
    #db_name = db_name + '.db'
    db = dataset.connect('sqlite:///database.db')

    # dumps csv file
    for table_name in db.tables:
        with open(table_name + '.csv', 'w') as csvfile:
            for row in db[table]:
                writer = csv.DictWriter(csvfile, fieldnames=db[table_name].columns)
                writer.writeheader()
                writer.writerow(row)
