
"""
functions:
sam_cell(seller, buyer, cell='quantity'), returns you the evolution over time of a cell
trade_over_time(seller, buyer, good, cell='quantity'), returns you the evolution over time of a cell
sam(t), returns the social accounting matrix at time t
sam_ext(t), returns the social accounting matrix at time t for every individual agent
"""
import os
import pylab
import numpy
import sqlite3
import csv


trade_unified = []  # placeholder value, since trade_unified seems to not have been defined in anywhere else

def to_r_and_csv(directory, db_name, csv=True): #pylint: disable=R0914
    os.chdir(directory)
    #db_name = db_name + '.db'
    c = sqlite3.CustomConnect('.', db_name)
    import glob
    print('--')
    print(db_name)
    print glob.glob("*")
    print glob.glob(db_name)
    table_names = c.executeQuery("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    table_names = [i for sublist in table_names for i in sublist] # equivalent to unlist, or numpy's ravel

    print("Import:")
    for i in table_names:
        c.execute("select * from %s" % i)
        table_contents = c.fetchall()
        column_names = [j[0] for j in c.description]
        column_types = [type(k) for k in table_contents[-1]]  # hack-ish, could have been done better @Rudy, I think this is pythonic
        print zip(column_names, column_types)
        print table_contents[1-3]

    for table in table_names:
        table_to_file(table, column_names, table_contents)

    for table in table_names:
        aggregate_and_convert(table, c)

    try: #MONKY PATCH why does this not work in python???, I numpy is not available in JYTHON, so NameError-try/catch is necessary
        tables = numpy.recarray(table_contents, dtype=zip(column_names, column_types)) #pylint: disable=E1101
    except (TypeError, ValueError) as e:
        print("irrelevant - numpy.recarray error: ", e)
        tables = [dict([(key, cell) for key, cell in zip(column_names, row)]) for row in table_contents]
    except NameError:
        tables = [dict([(key, cell) for key, cell in zip(column_names, row)]) for row in table_contents]
    c.close()

    if csv:
        #http://stackoverflow.com/questions/75675/how-do-i-dump-the-data-of-some-sqlite3-tables
        c.execute(".mode csv")
        c.execute(".header on")
        for table in table_names:
            c.execute(".out %s.csv" %table)
            c.execute("SELECT * from %s" %table)
        for table in new_tables:
            go("%s$round <- factor(%s$round)" % (table, table))
            go("%s$id <- factor(%s$id)" % (table, table))

        go("save(list = ls(all=TRUE), file = '%s')" % 'database.RData')
except ImportError:
    def to_r_and_csv(directory, basepath, csv=True):
        pass

def table_to_file(table_name, column_names, table_contents):
    with open(os.path.join('.', table_name + '.csv'), 'w') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(column_names)
        for row in table_contents:
            csv_writer.writerow(row)

def aggregate_and_convert(table, cursor):
    cursor.execute('SELECT * FROM %s' % table)
    column_names = [column_name[0] for column_name in cursor.description]
    if 'id' in column_names:
        with open(os.path.join('.', table + '_aggregate.csv'), 'w') as csv_file:
            csv_writer = csv.writer(csv_file)
            column_names.remove('id')
            column_names.remove('round')
            sum_string = ','.join('sum(%s)' % item for item in column_names)
            cursor.execute('SELECT round, ' + sum_string +' FROM ' + table + ' GROUP BY round;')
            csv_writer.writerow(['round'] + column_names)
            while True:
                try:
                    csv_writer.writerow(cursor.fetchone())
                except csv.Error:
                    break
