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
import threading
import sqlite3
from collections import defaultdict
from .online_variance import OnlineVariance
from postprocess import to_csv

class Database(threading.Thread):
    def __init__(self, directory, in_sok, trade_log):
        threading.Thread.__init__(self)
        self.directory = directory
        self.panels = {}
        self.aggregates = {}
        self.in_sok = in_sok
        self.data = {}
        self.trade_log = trade_log

        self.ex_str = {}
        self.aggregation = {}
        self.round = 0

    def add_trade_log(self):
        table_name = 'trade'
        self.database.execute("CREATE TABLE " + table_name +
                              "(round INT, good VARCHAR(50), seller VARCHAR(50), buyer VARCHAR(50), price FLOAT, quantity FLOAT)")
        return 'INSERT INTO trade (round, good, seller, buyer, price, quantity) VALUES (%i, "%s", "%s", "%s", "%s", %f)'

    def add_log(self, table_name):
        self.database.execute("CREATE TABLE log_" + table_name +
                              "(round INT, id INT, PRIMARY KEY(round, id))")

    def add_panel(self, group, column_names):
        self.panels['panel_' + group] = list(column_names)

    def add_aggregate(self, group, column_names):
        table_name = 'aggregate_' + group
        self.aggregation[table_name] = OnlineVariance(len(column_names))
        self.aggregates['aggregate_' + group] = list(column_names)
        self.aggregates['aggregate_' + group + '_mean'] = list(column_names)
        self.aggregates['aggregate_' + group + '_std'] = list(column_names)

    def run(self):
        self.db = sqlite3.connect(':memory:')
        self.database = self.db.cursor()
        self.database.execute('PRAGMA synchronous=OFF')
        self.database.execute('PRAGMA journal_mode=OFF')
        self.database.execute('PRAGMA count_changes=OFF')
        self.database.execute('PRAGMA temp_store=OFF')
        self.database.execute('PRAGMA default_temp_store=OFF')
        # self.database.execute('PRAGMA cache_size = -100000')
        if self.trade_log:
            trade_ex_str = self.add_trade_log()
        for table_name in self.panels:
            panel_str = ' FLOAT,'.join(self.panels[table_name]) + ' FLOAT,'

            create_str = "CREATE TABLE " + table_name + "(id INT, round INT, %s PRIMARY KEY(round, id))" % panel_str
            self.database.execute(create_str)

            format_strings = ','.join(['?'] * (2 + len(self.panels[table_name])))
            self.ex_str[table_name] = "INSERT INTO " + table_name + \
                "(id, round, " + ','.join(list(self.panels[table_name])) + ") VALUES (%s)" % format_strings

        for table_name in self.aggregates:
            agg_str = ' FLOAT,'.join(self.aggregates[table_name]) + ' FLOAT,'

            create_str = "CREATE TABLE " + table_name + "(round INT, %s PRIMARY KEY(round))" % agg_str
            self.database.execute(create_str)

            format_strings = ','.join(['?'] * (1 + len(self.aggregates[table_name])))
            self.ex_str[table_name] = "INSERT INTO " + table_name + \
                "(round, " + ','.join(list(self.aggregates[table_name])) + ") VALUES (%s)" % format_strings

        while True:
            try:
                msg = self.in_sok.get()
            except KeyboardInterrupt:
                to_csv(self.directory, self.db)
                break
            except EOFError:
                to_csv(self.directory, self.db)
                break
            if msg == "close":
                to_csv(self.directory, self.db)
                break

            elif msg[0] == 'panel':
                    table_name = 'panel_' + msg[1]
                    self.write_pa(table_name, msg[2])

            elif msg[0] == 'aggregate':
                round = msg[1]
                table_name = 'aggregate_' + msg[2]
                if self.round == round:
                    self.aggregation[table_name].update(msg[3])
                else:
                    self.write_pa(table_name, [self.round] + self.aggregation[table_name].sum())
                    self.write_pa(table_name + '_mean', [self.round] + self.aggregation[table_name].mean())
                    self.write_pa(table_name + '_std', [self.round] + self.aggregation[table_name].std())
                    self.aggregation[table_name].clear()
                    self.round = round
                    self.aggregation[table_name].update(msg[3])

            elif msg[0] == 'trade_log':
                individual_log = msg[1]
                round = msg[2]  # int
                for key in individual_log:
                    split_key = key[:].split(',')
                    self.database.execute(trade_ex_str % (round,
                                                          split_key[0], split_key[1], split_key[2], split_key[3],
                                                          individual_log[key]))
            elif msg[0] == 'log':
                group_name = msg[1]
                data_to_write = msg[2]
                try:
                    data_to_write = {key: float(
                        data_to_write[key]) for key in data_to_write}
                except TypeError:
                    print(data_to_write)
                    raise

                data_to_write['round'] = msg[3]
                table_name = 'log_' + group_name
                try:
                    self.write_or_update(table_name, data_to_write)
                except TableMissing:
                    self.add_log(group_name)
                    self.write(table_name, data_to_write)
                except sqlite3.InterfaceError:
                    raise Exception(
                        'InterfaceError: data can not be written. '
                        'If nested try: self.log_nested')
            else:
                raise Exception(
                    "abce_db error '%s' command unknown ~87" % msg)
        self.db.commit()
        self.db.close()

    def write_or_update(self, table_name, data_to_write):
        insert_str = "INSERT OR IGNORE INTO " + table_name + \
            "(" + ','.join(list(data_to_write.keys())) + ") VALUES (%s);"
        update_str = "UPDATE " + table_name + \
            " SET %s  WHERE CHANGES()=0 and round=%s and id=%s;"
        update_str = update_str % (','.join('%s=?' % key
                                   for key in data_to_write),
                                   data_to_write['round'],
                                   data_to_write['id'])
        rows_to_write = list(data_to_write.values())
        format_strings = ','.join(['?'] * len(rows_to_write))
        try:
            self.database.execute(insert_str % format_strings, rows_to_write)
        except sqlite3.OperationalError as e:
            errormsg = str(e)
            if 'no such table' in errormsg:
                raise TableMissing(table_name)
            if not('has no column named' in errormsg):
                raise
            self.new_column(table_name, data_to_write)
            self.write_or_update(table_name, data_to_write)
        self.database.execute(update_str, rows_to_write)

    def write_pa(self, table_name, rows_to_write):
        self.database.execute(self.ex_str[table_name], rows_to_write)

    def write(self, table_name, data_to_write):
        try:
            ex_str = "INSERT INTO " + table_name + \
                "(" + ','.join(list(data_to_write.keys())) + ") VALUES (%s)"
        except TypeError:
            raise TypeError("good names must be strings",
                            list(data_to_write.keys()))
        rows_to_write = list(data_to_write.values())
        format_strings = ','.join(['?'] * len(rows_to_write))
        try:
            self.database.execute(ex_str % format_strings, rows_to_write)
        except sqlite3.OperationalError as e:
            errormsg = str(e)
            if 'no such table' in errormsg:
                raise TableMissing(table_name)
            if not('has no column named' in errormsg):
                raise
            self.new_column(table_name, data_to_write)
            self.write(table_name, data_to_write)
        except sqlite3.InterfaceError:
            print((ex_str % format_strings, rows_to_write))
            raise

    def new_column(self, table_name, data_to_write):
        rows_to_write = list(data_to_write.values())
        self.database.execute("PRAGMA table_info(%s)" % table_name)
        existing_columns = [row[1] for row in self.database]
        new_columns = set(data_to_write.keys()).difference(existing_columns)
        for column in new_columns:
            try:
                if is_convertable_to_float(data_to_write[column]):
                    self.database.execute(" ALTER TABLE %s ADD %s FLOAT;"
                                          % (table_name, column))
                else:
                    self.database.execute(
                        " ALTER TABLE %s ADD %s VARCHAR(50);"
                        % (table_name, column))
            except TypeError:
                rows_to_write.remove(data_to_write[column])
                del data_to_write[column]

    def aggregate(self, table_name, data):
        for key in data:
            self.data[table_name][key].append(data[key])


class TableMissing(sqlite3.OperationalError):
    def __init__(self, message):
        super(TableMissing, self).__init__(message)


def is_convertable_to_float(x):
    try:
        float(x)
    except TypeError:
        if not(x):
            raise TypeError
        return False
    return True


def _number_or_string(word):
    """ returns a int if possible otherwise a float from a string
    """
    try:
        return int(word)
    except ValueError:
        try:
            return float(word)
        except ValueError:
            return word
