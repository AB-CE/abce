import os
from collections import defaultdict
import csv


def to_csv(directory, dataset):
    os.chdir(directory)
    tables = dataset.tables
    panels = defaultdict(list)
    aggs = defaultdict(list)
    for table_name in tables:
        typ = table_name.split('___')[0]
        group = table_name.split('___')[1]
        if typ == 'panel':
            panels[group].append(table_name)
        elif typ == 'aggregate':
            aggs[group].append(table_name)
        elif typ == 'trade':
            print([ds for ds in dataset[table_name].all()][0])
            save_to_csv('trade_', '_trade', dataset)

    for group, tables in aggs.items():
        join_table(tables, group, 'round', 'aggregate', dataset)

    for group, tables in panels.items():
        join_table(tables, group, 'name, round', 'panel', dataset)
        create_aggregated_table(group, dataset)
    dataset.commit()

    for group in aggs:
        save_to_csv('aggregate', group, dataset)

    for group in panels:
        save_to_csv('panel', group, dataset)
        save_to_csv('aggregated', group, dataset)
    os.chdir('../..')


def create_aggregated_table(group, dataset):
    columns = ', '.join('AVG(%s) %s_mean, SUM(%s) %s_ttl' % (c, c, c, c)
                        for c in get_columns(dataset, 'panel_%s' % group))
    try:
        dataset.query("CREATE TABLE aggregated_%s AS "
                      "SELECT round, %s FROM panel_%s GROUP BY round ORDER BY cast(round as float);"
                      % (group, columns, group))
    except Exception:
        print('round not castable as float; default to unordered group by')
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
            if c not in ('index', 'name', 'round')]
