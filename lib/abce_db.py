""" must be imported with ' from agentengine import * ' by all agents """
import zmq
import multiprocessing
from collections import defaultdict
import sqlite3
from os import path
import csv


class Database(multiprocessing.Process):
    def __init__(self,directory, db_name):
        multiprocessing.Process.__init__(self)
        self.db = sqlite3.connect(path.join(directory,db_name + '.db'))
        self.database = self.db.cursor()
        self.index = defaultdict(lambda: 0)
        self.round = 0

    def add_panel(self, group, command):
        table_name = command + '_' + group
        self.database.execute("CREATE TABLE " + table_name + "(round INT, id INT, i INT)")


    def add_follow(self, name):
        self.database.execute("CREATE TABLE " + name[0:-1] + "(round INT, command VARCHAR(50), name VARCHAR(50), i INT)")

    def run(self):
        context = zmq.Context()
        in_sok = context.socket(zmq.SUB)
        in_sok.connect("ipc://backend.ipc")
        in_sok.setsockopt(zmq.SUBSCRIBE, "db_agent:")
        self.index = defaultdict(lambda: 0)
        while True:
            address_command = in_sok.recv()
            if address_command == "db_agent:close":
                self.db.close()
                break
            if address_command == "db_agent:advance_round":
                self.round += 1
                print('(' + str(self.round) + ')')
                self.db.commit()
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
            else:
                name = in_sok.recv()[0:-1]
                command = in_sok.recv()
                self.index[name] += 1
                data_to_write = in_sok.recv_json()
                data_to_write['name'] = name
                data_to_write['command'] = command
                data_to_write['round'] = self.round
                data_to_write['i'] = self.index[name]
                self.write(name, data_to_write)

    def write(self, table_name, data_to_write):
        rows_to_write = data_to_write.values()
        ex_str = "INSERT INTO " + table_name + "(" + ','.join(data_to_write.keys()) + ") VALUES (%s)"
        format_strings = ','.join(['?'] * len(rows_to_write))
        try:
            self.database.execute(ex_str % format_strings, rows_to_write)
        except sqlite3.OperationalError, msg:
            if not('has no column named' in msg.message):
                raise
            self.database.execute("""PRAGMA table_info(""" + table_name + """)""")
            existing_columns = [row[1] for row in self.database]
            new_columns = set(data_to_write.keys()).difference(existing_columns)
            for column in new_columns:
                self.database.execute(""" ALTER TABLE """ + table_name + """ ADD """ + column + """ FLOAT;""")
            self.database.execute(ex_str % format_strings, rows_to_write)


def convert_to_csv(directory, db_name):
    conn = sqlite3.connect(path.join(directory, db_name + '.db'))
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    for table in tables:
        table = table[0]
        cursor.execute('SELECT * FROM ' + table)
        column_names = [column_name[0] for column_name in cursor.description]
        with open(path.join(directory, table + '.csv'), 'w') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(column_names)
            while True:
                try:
                    csv_writer.writerow(cursor.fetchone())
                except csv.Error:
                    break
        if 'id' in column_names:
            with open(path.join(directory, table + '_aggregate.csv'), 'w') as csv_file:
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