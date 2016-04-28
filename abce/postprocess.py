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
        try:
            table = pd.read_sql_query("SELECT * from %s" % table_name, db)
        except:
            print("most likely your pip installation is not up to date.")
            print("If you are on ubuntu/linux type:")
            print()
            print("sudo apt-get purge python-pandas")
            print("sudo pip uninstall pandas")
            print("sudo apt-get install python-setuptools python-dev build-essential")
            print("sudo pip install pandas")
            print()
            print("If you keep having problems email davoudtaghawinejad@gmail.com")
            raise
        table.to_csv(table_name + '.csv', index_label='index')
        if u'id' in table.columns:
            del table['id']
            grouped = table.groupby('round')
            aggregated = grouped.sum()
            try:
                meaned = grouped.mean()
                meaned.rename(columns={col: col + '_mean' for col in meaned.columns}, inplace=True)
            except pd.core.groupby.DataError:
                pass
            try:
                std = grouped.std()
                std.rename(columns={col: col + '_std' for col in std.columns}, inplace=True)
            except:
                pass

            result = pd.concat([aggregated, meaned, std], axis=1)

            result.to_csv('aggregate_' + table_name + '.csv', index_label='index')

    os.chdir('../..')
