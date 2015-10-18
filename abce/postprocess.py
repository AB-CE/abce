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
            aggregated.to_csv(table_name + '_aggregate.csv', index_label='index')
            try:
                meaned = grouped.mean()
                meaned.to_csv(table_name + '_mean.csv', index_label='index')
            except pd.core.groupby.DataError:
                pass
