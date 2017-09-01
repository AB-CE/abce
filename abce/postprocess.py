import os
from collections import defaultdict
import csv


def to_csv(directory, db):
    os.chdir(directory)
    cursor = db.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    for table_name in tables:
        table_name = table_name[0]
        try:
            table = pd.read_sql_query("SELECT * from %s" % table_name, db)
        except:
            raise Exception("your pip installation is not up to date.")

        if 'round' in table.columns:
            table.to_csv(table_name + '.csv', index_label='index')
        else:
            table.to_csv(table_name + '.csv', index_label='round')

        if u'id' in table.columns:
            del table['id']
            grouped = table.groupby('round')
            aggregated = grouped.sum()
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
            result.to_csv('aggregate_' + table_name + '.csv',
                          index_label='round', date_format='%Y-%m-%d')

    for group in panels:
        save_to_csv('panel', group, dataset)
        save_to_csv('aggregated', group, dataset)
    os.chdir('../..')


def create_aggregated_table(group, dataset):
    columns = ', '.join('AVG(%s) %s_mean, SUM(%s) %s_ttl' % (c, c, c, c)
                        for c in get_columns(dataset, 'panel_%s' % group))
    dataset.query("CREATE TABLE aggregated_%s AS "
                  "SELECT round, %s FROM panel_%s GROUP BY round;"
                  % (group, columns, group))
    dataset.update_table('aggregated_%s' % group)


def join_table(tables, group, indexes, type_, dataset):
    for i, table_name in enumerate(tables):
        if i == 0:
            dataset.query("CREATE TEMPORARY TABLE temp0 AS "
                          "SELECT * FROM %s;" % table_name)
        else:
            redundant_columns = (set(dataset[table_name].columns) &
                                 set(dataset['temp%i' % (i - 1)].columns))
            dataset.query("CREATE TEMPORARY TABLE temp%i AS "
                          "SELECT temp%i.* %s "
                          "FROM temp%i LEFT JOIN %s using(%s)"
                          % (i, i - 1,
                             get_str_columns(dataset, table_name,
                                             redundant_columns),
                             i - 1, table_name, indexes))
            dataset.query("DROP TABLE temp%i;" % (i - 1))
        dataset.query("DROP TABLE %s" % table_name)

    dataset.query("CREATE TABLE %s_%s AS "
                  "SELECT * FROM temp%i" % (type_, group, i))
    dataset.update_table('panel_%s' % group)
    dataset.query("DROP TABLE temp%i;" % i)


def save_to_csv(prefix, group, dataset):
    table = dataset['%s_%s' % (prefix, group)]
    with open('%s_%s.csv' % (prefix, group), 'w') as outfile:
        outdict = csv.DictWriter(outfile, fieldnames=table.columns)
        outdict.writeheader()
        for row in table:
            outdict.writerow(row)


def get_str_columns(dataset, table_name, redundant_columns):
    ret = ', '.join([' %s ' % c
                     for c in dataset[table_name].columns
                     if c not in list(redundant_columns)])
    if ret == '':
        return ''
    else:
        return ', %s' % ret


def get_columns(dataset, table_name):
    return [c for c in dataset[table_name].columns
            if c not in ('index', 'id', 'round')]
