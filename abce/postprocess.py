import os
import pylab

trade_unified = []  # placeholder value, since trade_unified seems to not have been defined in anywhere else
#postprocess.R
"""
functions:
sam_cell(seller, buyer, cell='quantity'), returns you the evolution over time of a cell
trade_over_time(seller, buyer, good, cell='quantity'), returns you the evolution over time of a cell
sam(t), returns the social accounting matrix at time t
sam_ext(t), returns the social accounting matrix at time t for every individual agent
"""
def sam_cell(seller, buyer, cell='quantity', target=trade_unified):
    return target[which (trade_unified[seller]==seller & trade_unified[buyer]==buyer),('round', cell)]

def trade_over_time(seller, buyer, good, cell='quantity'):
    return trade_unified[which (trade_unified[seller]==seller & trade_unified[buyer]==buyer & trade_unified[good]==good),('round', cell)]

def sam(t=0, target=trade_unified, value='quantity'):
    cast(target[which(target[round] == t),], seller + good , buyer, sum, margins=c("grand_row","grand_col"), value=value)

def sam_ext(t=1):
    return cast(trade[which(trade[round] == t),], seller + good , buyer, sum, margins=("grand_row","grand_col"))


def to_r_and_csv(directory, basepath, csv=True):
    os.chdir(directory)
    print(__file__)
    #table_names, table_contents = go()
    import sqlite3
    con = sqlite3.connect('database.db')
    c = con.cursor()
    table_names = c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    table_names = [i for sublist in table_names for i in sublist] # equivalent to unlist, or numpy's ravel


    print("Import:")
    #con.row_factory = sqlite3.Row #dict_factory
    for i in table_names:
        c.execute("select * from %s" %i)
        table_contents = c.fetchall()
        table_ids = [j[0] for j in c.description]
        table_types = [type(k) for k in table_contents[-1]]  # hack-ish, could have been done better
        #table_types = [int, str, str, str, float, float]
        print zip(table_ids, table_types)
        print table_contents
        tables = pylab.recarray(table_contents, dtype=zip(table_ids, table_types))
    #con.close()

    all_tables = dict(zip(table_names, tables))

    try:
        del all_tables['trade_unified']
    #except KeyError:
    except:
        pass
    new_tables = set()
    for table_name in all_tables.keys():
        table = all_tables[table_name]
        names = table_name.split('_')
        underscore_index = table_name.find('_')
        if underscore_index != -1:
            new_tables.add(names[0])
            name = table[underscore_index+1:]
            columns = table.keys()
            columns = [col for col in columns if not(col in ('round', 'id'))]
            for col in columns:
                if names[0]==col:
                    table['%s_%s] %'(name, col)] = table.pop(col)

    import numpy.lib.recfunctions as rfn
    for table_name in new_tables:
        acquisitions = c.execute("SELECT * FROM (SELECT name FROM sqlite_master WHERE type='table') WHERE name REGEXP '%s_.*'" % table_name).fetchall()
        print 'acquisitions',acquisitions
        go("%s <- %s[c('round', 'id')]" % (table, acquisitions[0]))
        for acq in acquisitions:
            table = rfn.rec_join(['round','id'], table, acq)

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
