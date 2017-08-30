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

    for group, tables in aggs.items():
        for i, table_name in enumerate(tables):
            if i == 0:
                dataset.query("CREATE TEMPORARY TABLE temp0 AS "
                              "SELECT * FROM %s;" % table_name)
            else:
                dataset.query("CREATE TEMPORARY TABLE temp%i AS "
                              "SELECT temp%i.*, %s "
                              "FROM temp%i LEFT JOIN %s using(id, round)"
                              % (i, i - 1,
                                 get_str_columns(dataset, table_name),
                                 i, table_name))
                dataset.query("DROP TABLE temp%i;" % (i - 1))
            dataset.query("DROP TABLE %s" % table_name)

        dataset.query("CREATE TABLE aggregate_%s AS "
                      "SELECT * FROM temp%i" % (group, i))
        dataset.update_table('panel_%s' % group)
        dataset.query("DROP TABLE temp%i;" % i)

    for group, tables in panels.items():
        for i, table_name in enumerate(tables):
            if i == 0:
                dataset.query("CREATE TEMPORARY TABLE temp0 AS "
                              "SELECT * FROM %s;" % table_name)
            else:
                dataset.query("CREATE TEMPORARY TABLE temp%i AS "
                              "SELECT temp%i.*, %s "
                              "FROM temp%i LEFT JOIN %s using(id, round)"
                              % (i, i - 1,
                                 get_str_columns(dataset, table_name),
                                 i - 1, table_name))
                dataset.query("DROP TABLE temp%i;" % (i - 1))
            dataset.query("DROP TABLE %s" % table_name)

        dataset.query("CREATE TABLE panel_%s AS "
                      "SELECT * FROM temp%i" % (group, i))
        dataset.update_table('panel_%s' % group)
        dataset.query("DROP TABLE temp%i;" % i)

        columns = ', '.join('AVG(%s) %s_mean, SUM(%s) %s_ttl' % (c, c, c, c)
                            for c in get_columns(dataset, 'panel_%s' % group))
        dataset.query("CREATE TABLE aggregated_%s AS "
                      "SELECT round, %s FROM panel_%s GROUP BY round;"
                      % (group, columns, group))
        dataset.update_table('aggregated_%s' % group)
        dataset.commit()

        for group in aggs:
            save_to_csv('aggregate', group, dataset)

        for group in panels:
            save_to_csv('panel', group, dataset)
            save_to_csv('aggregated', group, dataset)
            pass

    os.chdir('../..')


def save_to_csv(prefix, group, dataset):
    table = dataset['%s_%s' % (prefix, group)]
    with open('%s_%s.csv' % (prefix, group), 'w') as outfile:
        outdict = csv.DictWriter(outfile, fieldnames=table.columns)
        outdict.writeheader()
        for row in table:
            outdict.writerow(row)


def get_str_columns(dataset, table_name):
    return ', '.join([' %s ' % c
                      for c in dataset[table_name].columns
                      if c not in ('index', 'id', 'round')])


def get_columns(dataset, table_name):
    return [c for c in dataset[table_name].columns
            if c not in ('index', 'id', 'round')]
