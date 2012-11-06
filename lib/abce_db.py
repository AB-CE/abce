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
import zmq
import multiprocessing
import sqlite3
import numpy as np


class Database(multiprocessing.Process):
    def __init__(self, directory, db_name, _addresses):
        multiprocessing.Process.__init__(self)
        self.db = sqlite3.connect(directory + '/' + db_name + '.db')
        self.database = self.db.cursor()
        self.database.execute('PRAGMA synchronous=OFF')
        self.database.execute('PRAGMA journal_mode=OFF')
        self.database.execute('PRAGMA count_changes=OFF')
        self.database.execute('PRAGMA temp_store=OFF')
        self.database.execute('PRAGMA default_temp_store=OFF')
        for t in (np.int8, np.int16, np.int32, np.int64,
                                    np.uint8, np.uint16, np.uint32, np.uint64):
            sqlite3.register_adapter(t, long)
        self._addresses = _addresses

    def add_trade_log(self):
        table_name = 'trade'
        self.database.execute("CREATE TABLE " + table_name +
            "(round INT, good VARCHAR(50), seller VARCHAR(50), buyer VARCHAR(50), price FLOAT, quantity FLOAT)")
        return 'INSERT INTO trade (round, good, seller, buyer, price, quantity) VALUES (%i, "%s", "%s", "%s", "%s", %f)'

    def add_log(self, table_name):
        self.database.execute("CREATE TABLE " + table_name + "(round INT, id INT, PRIMARY KEY(round, id))")

    def add_panel(self, group, command):
        table_name = command + '_' + group
        self.database.execute("CREATE TABLE " + table_name + "(round INT, id INT, PRIMARY KEY(round, id))")

    def run(self):
        context = zmq.Context()
        in_sok = context.socket(zmq.PULL)
        in_sok.bind(self._addresses['database'])
        trade_ex_str = self.add_trade_log()
        while True:
            typ = in_sok.recv()
            if typ == "close":
                break
            if typ == 'panel':
                command = in_sok.recv()
                data_to_write = in_sok.recv_pyobj()
                data_to_write['id'] = int(in_sok.recv())
                group = in_sok.recv()
                data_to_write['round'] = int(in_sok.recv())
                table_name = command + '_' + group
                self.write(table_name, data_to_write)
            elif typ == 'trade_log':
                individual_log = in_sok.recv_pyobj()
                round = int(in_sok.recv())
                for key in individual_log:
                    split_key = key[:].split(',')
                    self.database.execute(trade_ex_str % (round,
                                                        split_key[0], split_key[1], split_key[2], split_key[3],
                                                        individual_log[key]))
            elif typ == 'log':
                group_name = in_sok.recv()
                data_to_write = in_sok.recv_pyobj()
                data_to_write['round'] = int(in_sok.recv())
                table_name = group_name
                try:
                    self.write_or_update(table_name, data_to_write)
                except TableMissing:
                    self.add_log(group_name)
                    self.write(table_name, data_to_write)
                except sqlite3.InterfaceError:
                    print(table_name, data_to_write)
                    SystemExit('InterfaceError: data can not be written. If nested try: self.log_nested')
            else:
                raise SystemExit('abce_db error %s command unknown ~87' % typ)
        self.db.commit()
        self.db.close()
        context.destroy()

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
        except sqlite3.InterfaceError:
            print(ex_str % format_strings, rows_to_write)
            raise

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

