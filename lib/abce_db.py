# Copyright 2012 Davoud Taghawi-Nejad
#
# Module Author: Davoud Taghawi-Nejad
#
# ABCE is open-source software. If you are using ABCE for your research you are
# requested the quote the use of this software.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License and quotation of the
# author. You may obtain a copy of the License at
#       http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.
""" must be imported with ' from agentengine import * ' by all agents """
import zmq
import multiprocessing
from collections import defaultdict
import sqlite3
from os import path
import csv


class Database(multiprocessing.Process):
    def __init__(self, directory, db_name):
        multiprocessing.Process.__init__(self)
        self.db = sqlite3.connect(path.join(directory, db_name + '.db'))
        self.database = self.db.cursor()
        self.round = 0

    def add_trade_log(self):
        table_name = 'trade'
        self.database.execute("CREATE TABLE " + table_name +
            "(round INT, seller VARCHAR(50), buyer VARCHAR(50), good VARCHAR(50), price FLOAT, quantity FLOAT)")
        return "INSERT INTO trade (round, good, seller, buyer, price, quantity) VALUES (?,?,?,?,?,?)"

    def add_log(self, table_name):
        self.database.execute("CREATE TABLE " + table_name + "(round INT, id INT, PRIMARY KEY(round, id))")

    def add_panel(self, group, command):
        table_name = command + '_' + group
        self.database.execute("CREATE TABLE " + table_name + "(round INT, id INT, PRIMARY KEY(round, id))")

    def run(self):
        context = zmq.Context()
        in_sok = context.socket(zmq.SUB)
        in_sok.connect("ipc://backend.ipc")
        in_sok.setsockopt(zmq.SUBSCRIBE, "db_agent:")
        trade_ex_str = self.add_trade_log()
        trade_log = defaultdict(int)
        while True:
            address_command = in_sok.recv()
            if address_command == "db_agent:close":
                self.db.close()
                break
            if address_command == "db_agent:advance_round":
                print('(' + str(self.round) + ')')
                for key in trade_log:
                    self.database.execute(trade_ex_str, [self.round] + key.split(',') + [trade_log[key]])
                trade_log = defaultdict(int)
                self.db.commit()
                self.round += 1
                continue
            typ = in_sok.recv()
            if typ == 'panel':
                idn = int(in_sok.recv())
                command = in_sok.recv()
                group = in_sok.recv()
                data_to_write = in_sok.recv_json()
                data_to_write['round'] = self.round
                data_to_write['id'] = idn
                table_name = command + '_' + group
                self.write(table_name, data_to_write)
            elif typ == 'trade_log':
                individual_log = in_sok.recv_json()
                for key in individual_log:
                    trade_log[key] += individual_log[key]
            elif typ == 'log':
                group_name = in_sok.recv()
                data_to_write = in_sok.recv_json()
                data_to_write['round'] = self.round
                table_name = group_name
                try:
                    self.write_or_update(table_name, data_to_write)
                except TableMissing:
                    self.add_log(group_name)
                    self.write(table_name, data_to_write)

    def write_or_update(self, table_name, data_to_write):
        insert_str = "INSERT OR IGNORE INTO " + table_name + "(" + ','.join(data_to_write.keys()) + ") VALUES (%s);"
        update_str = "UPDATE " + table_name + " SET %s  WHERE CHANGES()=0 and round=%s and id=%s;"
        update_str = update_str % (','.join('%s=?' % key for key in data_to_write),
            data_to_write['round'], data_to_write['id'])
        rows_to_write = data_to_write.values()
        format_strings = ','.join(['?'] * len(rows_to_write))
        try:
            self.database.execute(insert_str % format_strings, rows_to_write)
        except sqlite3.OperationalError, msg:
            if 'no such table' in msg.message:
                raise TableMissing
            if not('has no column named' in msg.message):
                raise
            self.new_column(table_name, data_to_write)
            self.write_or_update(table_name, data_to_write)
        self.database.execute(update_str, rows_to_write)

    def write(self, table_name, data_to_write, ex_str=''):
        ex_str = "INSERT INTO " + table_name + "(" + ','.join(data_to_write.keys()) + ") VALUES (%s)"
        rows_to_write = data_to_write.values()
        format_strings = ','.join(['?'] * len(rows_to_write))
        try:
            self.database.execute(ex_str % format_strings, rows_to_write)
        except sqlite3.OperationalError, msg:
            if 'no such table' in msg.message:
                raise TableMissing
            if not('has no column named' in msg.message):
                raise
            self.new_column(table_name, data_to_write)
            self.write(table_name, data_to_write)

    def new_column(self, table_name, data_to_write):
        rows_to_write = data_to_write.values()
        self.database.execute("""PRAGMA table_info(""" + table_name + """)""")
        existing_columns = [row[1] for row in self.database]
        new_columns = set(data_to_write.keys()).difference(existing_columns)
        for column in new_columns:
            try:
                if is_convertable_to_float(data_to_write[column]):
                    self.database.execute(""" ALTER TABLE """ + table_name + """ ADD """ + column + """ FLOAT;""")
                else:
                    self.database.execute(""" ALTER TABLE """ + table_name + """ ADD """ + column + """ VARCHAR(50);""")
            except TypeError:
                rows_to_write.remove(data_to_write[column])
                del data_to_write[column]


class TableMissing(sqlite3.OperationalError):
    pass


def is_convertable_to_float(x):
    try:
        float(x)
    except TypeError:
        if not(x):
            raise TypeError
        return False
    return True


def convert_to_csv(directory, db_name):
    def write_differences(table, stock_name='_diff'):
        cursor.execute('PRAGMA table_info(%s);' % table)
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]
        if column_names.count('id'):
            write_panel_diff(table, stock_name)
        else:
            write_aggregate_diff(table, stock_name)

    def write_panel_diff(table, stock_name='_diff'):
        file_path_and_name = path.join(directory, table + '_' + stock_name + '.csv')
        cursor.execute('PRAGMA table_info(%s);' % table)
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]
        columns_to_delta = []
        for column in columns:
            if column[1] == u'round':
                col_round = column[0]
            if column[1] == u'id':
                col_id = column[0]
            if (column[2] == u'INT' or column[2] == u'FLOAT') \
                and column[1] != 'round' and column[1] != 'id':
                columns_to_delta.append(column[0])
        with open(file_path_and_name, 'w') as csv_file:
            csv_writer = csv.writer(csv_file, dialect='excel-tab')
            cursor.execute('SELECT * FROM ' + table + ';')
            csv_writer.writerow(column_names)
            data = cursor.fetchall()
            data_by_rounds = defaultdict(lambda: {})
            for row in data:
                data_by_rounds[(row[col_round], row[col_id])] = row
            for row in data:
                last_round = row[col_round] - 1
                if not((last_round, row[col_id]) in data_by_rounds):
                    continue
                delta = []
                for x in range(len(row)):
                    if x in columns_to_delta:
                        try:
                            delta.append(row[x] - data_by_rounds[(last_round, row[col_id])][x])
                        except TypeError:
                            if row[x] is not None and \
                                data_by_rounds[(last_round, row[col_id])][x] is not None:
                                raise
                            else:
                                delta.append(None)
                        except KeyError:
                            print(data_by_rounds[last_round][row[col_id]])
                    else:
                        delta.append(row[x])
                csv_writer.writerow(delta)

    def write_aggregate_diff(table, stock_name):
        file_path_and_name = path.join(directory, table + '_' + stock_name + '.csv')
        cursor.execute('PRAGMA table_info(%s);' % table)
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]
        columns_to_delta = []
        for column in columns:
            if column[1] == u'round':
                col_round = column[0]
            if (column[2] == u'INT' \
                or column[2] == u'FLOAT' \
                or column[2] == u'') \
                and column[1] != 'round':
                columns_to_delta.append(column[0])
        with open(file_path_and_name, 'w') as csv_file:
            csv_writer = csv.writer(csv_file, dialect='excel-tab')
            cursor.execute('SELECT * FROM ' + table + ';')
            csv_writer.writerow(column_names)
            data = cursor.fetchall()
            data_by_rounds = defaultdict(lambda: {})
            for row in data:
                data_by_rounds[row[col_round]] = row
            for row in data:
                last_round = row[col_round] - 1
                if not(last_round in data_by_rounds):
                    continue
                delta = []
                for x in range(len(row)):
                    if x in columns_to_delta:
                        try:
                            delta.append(row[x] - data_by_rounds[last_round][x])
                        except TypeError:
                            if row[x] is not None and \
                                data_by_rounds[last_round][x] is not None:
                                raise
                            else:
                                delta.append(None)
                    else:
                        delta.append(row[x])
                csv_writer.writerow(delta)

    def write_aggregate(table, agg_name, group_by):
        file_path_and_name = path.join(directory, table + '_' + agg_name + '.csv')
        cursor.execute('PRAGMA table_info(%s);' % table)
        columns = cursor.fetchall()
        columns_to_sum = []
        columns_to_show = group_by
        for column in columns:
            if (column[2] == u'INT' or column[2] == u'FLOAT') \
                and column[1] != 'round' and column[1] != 'id':
                columns_to_sum.append(column[1])
        sum_string = ','.join('sum(%s)' % item for item in columns_to_sum)
        show_string = ','.join(columns_to_show)
        with open(file_path_and_name, 'w') as csv_file:
            csv_writer = csv.writer(csv_file, dialect='excel-tab')
            cursor.execute('SELECT ' + show_string + ',' + sum_string + \
                ' FROM ' + table + ' GROUP BY ' + ','.join(group_by) + ';')
            csv_writer.writerow(columns_to_show + columns_to_sum)
            while True:
                try:
                    csv_writer.writerow(cursor.fetchone())
                except csv.Error:
                    break
        new_table_name = table + '_' + agg_name
        cursor.execute('CREATE TABLE ' + new_table_name + ' AS '
            'SELECT ' + show_string + ',' + sum_string + \
                ' FROM ' + table + ' GROUP BY ' + ','.join(group_by) + ' ;')
        return new_table_name

    def write_table(table):
        cursor.execute('SELECT * FROM ' + table)
        column_names = [column_name[0] for column_name in cursor.description]
        with open(path.join(directory, table + '.csv'), 'w') as csv_file:
            csv_writer = csv.writer(csv_file, dialect='excel-tab')
            csv_writer.writerow(column_names)
            while True:
                try:
                    csv_writer.writerow(cursor.fetchone())
                except csv.Error:
                    break

    conn = sqlite3.connect(path.join(directory, db_name + '.db'))
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    for table in tables:
        table = table[0]
        write_table(table)
        column_names = [column_name[0] for column_name in cursor.description]
        if 'id' in column_names:
            agg = write_aggregate(table, 'aggregate', group_by=['round'])
            write_differences(agg, 'diff')
        write_differences(table, 'diff')
