import os
import sqlite3
from collections import defaultdict


def to_csv(directory):
    os.chdir(directory)
    database = sqlite3.connect('dataset.db')
    cursor = database.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    panels = defaultdict(list)
    aggs = defaultdict(list)
    for table_name in tables:
        table_name = table_name[0]
        typ = table_name.split('___')[0]
        group = table_name.split('___')[1]
        if typ == 'panel':
            panels[group].append(table_name)
        elif typ == 'aggregate':
            aggs[group].append(table_name)

    for group, tables in aggs.items():
        for i, table_name in enumerate(tables):
            if i == 0:
                cursor.execute("CREATE TEMPORARY TABLE temp0 AS "
                               "SELECT * FROM %s;" % table_name)
            else:
                cursor.execute("CREATE TEMPORARY TABLE temp%i AS "
                               "SELECT temp%i.*, %s "
                               "FROM temp%i LEFT JOIN %s using(id, round)"
                               % (i, i - 1,
                                  get_str_columns(cursor, table_name),
                                  i, table_name))
                cursor.execute("DROP TABLE temp%i;" % (i - 1))
            cursor.execute("DROP TABLE %s" % table_name)

        cursor.execute("CREATE TABLE aggregate_%s AS "
                       "SELECT * FROM temp%i" % (group, i))
        cursor.execute("DROP TABLE temp%i;" % i)

    for group, tables in panels.items():
        for i, table_name in enumerate(tables):
            if i == 0:
                cursor.execute("CREATE TEMPORARY TABLE temp0 AS "
                               "SELECT * FROM %s;" % table_name)
            else:
                cursor.execute("CREATE TEMPORARY TABLE temp%i AS "
                               "SELECT temp%i.*, %s "
                               "FROM temp%i LEFT JOIN %s using(id, round)"
                               % (i, i - 1,
                                  get_str_columns(cursor, table_name),
                                  i - 1, table_name))
                cursor.execute("DROP TABLE temp%i;" % (i - 1))
            cursor.execute("DROP TABLE %s" % table_name)

        cursor.execute("CREATE TABLE panel_%s AS "
                       "SELECT * FROM temp%i" % (group, i))
        cursor.execute("DROP TABLE temp%i;" % i)

        columns = ', '.join('AVG(%s) %s_mean, SUM(%s) %s_ttl' % (c, c, c, c)
                            for c in get_columns(cursor, 'panel_%s' % group))
        cursor.execute("CREATE TABLE aggregated_%s AS "
                       "SELECT round, %s FROM panel_%s GROUP BY round;"
                       % (group, columns, group))
        database.commit()

    os.chdir('../..')


def get_str_columns(cursor, table_name):
    cursor.execute("PRAGMA table_info('%s')" % table_name)
    return ', '.join([' %s ' % c[1]
                      for c in cursor
                      if c[1] not in ('index', 'id', 'round')])


def get_columns(cursor, table_name):
    cursor.execute("PRAGMA table_info('%s')" % table_name)
    return [c[1] for c in cursor if c[1] not in ('index', 'id', 'round')]
