import os
import sqlite3
import pandas as pd
from collections import defaultdict


def to_csv(directory):
    os.chdir(directory)
    database = sqlite3.connect('dataset.db')
    cursor = database.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    panel = defaultdict(pd.DataFrame)
    aggs = defaultdict(pd.DataFrame)
    for table_name in tables:
        table_name = table_name[0]
        table = pd.read_sql_query("SELECT * from %s" % table_name, database)

        typ = table_name.split('___')[0]
        group = table_name.split('___')[1]
        if typ == 'panel':
            panel[group] = pd.concat([panel[group], table], axis=1)
        elif typ == 'aggregate':
            aggs[group] = pd.concat([aggs[group], table], axis=1)
        elif typ == 'trade':
            table.to_csv('trade.csv', index=False)

    for group, df in aggs.items():
        df = df.loc[:, ~df.columns.duplicated()]
        df.to_csv('aggregate_' + group + '.csv', index=False)

    for group, df in panel.items():
        df = df.loc[:, ~df.columns.duplicated()]
        df.to_csv(group + '.csv', index=False)

        if u'id' in df:
            del df['id']
        grouped = df.groupby('round')
        aggregated = grouped.sum()
        aggregated.rename(
            columns={col: col + '_ttl'
                     for col in aggregated.columns}, inplace=True)
        try:
            meaned = grouped.mean()
            meaned.rename(
                columns={col: col + '_mean'
                         for col in meaned.columns}, inplace=True)
        except pd.core.groupby.DataError:
            meaned = pd.DataFrame()
        try:
            std = grouped.std()
            std.rename(
                columns={col: col + '_std'
                         for col in std.columns}, inplace=True)
        except pd.core.groupby.DataError:
            std = pd.DataFrame()

        result = pd.concat([aggregated, meaned, std], axis=1)
        result.to_csv('aggregated_' + group + '.csv',
                      index_label='round')
    os.chdir('../..')
