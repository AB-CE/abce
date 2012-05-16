""" must be imported with ' from agentengine import * ' by all agents """
import zmq
import multiprocessing
from abce_common import agent_name, group_address
from collections import defaultdict
import sqlite3

class Database(multiprocessing.Process):
    def __init__(self, db_name):
        multiprocessing.Process.__init__(self)
        self.db = sqlite3.connect(db_name + '.db')
        self.database = self.db.cursor()
        self.index = defaultdict(lambda: 0)
        self.round = 0

    def add_panel(self, group, command):
        table_name = command + '_' + group
        begin = "INSERT INTO " + table_name + "(round, id,"
        values = ") VALUES (%s)"
        ex_str = "CREATE TABLE " + table_name + "(round INT, id INT, i INT)"
        self.database.execute(ex_str)


    def add_follow(self, name):
        ex_str = "CREATE TABLE " + name[0:-1] + "(round INT, command VARCHAR(50), name VARCHAR(50), i INT)"
        self.database.execute(ex_str)

    def run(self):
        context = zmq.Context()
        self.in_sok = context.socket(zmq.SUB)
        self.in_sok.connect("ipc://backend.ipc")
        self.in_sok.setsockopt(zmq.SUBSCRIBE, "db_agent:")
        self.index = defaultdict(lambda: 0)
        while True:
            address_command = self.in_sok.recv()
            if address_command == "db_agent:close":
                self.db.close()
                break
            if address_command == "db_agent:advance_round":
                self.round += 1
                print('(' + str(self.round) + ')')
                continue
            typ = self.in_sok.recv()
            if typ == 'panel':
                idn = int(self.in_sok.recv())
                command = self.in_sok.recv()
                group = self.in_sok.recv()
                data_to_write = self.in_sok.recv_json()
                data_to_write['round'] = self.round
                data_to_write['id'] = idn
                table_name = command + '_' + group
                self.write(table_name, data_to_write)
            else:
                name = self.in_sok.recv()[0:-1]
                command = self.in_sok.recv()
                self.index[name] += 1
                data_to_write = self.in_sok.recv_json()
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
        except (TypeError, sqlite3.OperationalError):
            self.database.execute("""PRAGMA table_info(""" + table_name + """)""")
            existing_columns = [row[1] for row in self.database]
            new_columns = set(data_to_write.keys()).difference(existing_columns)
            for column in new_columns:
                self.database.execute(""" ALTER TABLE """ + table_name + """ ADD """ + column + """ FLOAT;""")
            self.database.execute(ex_str % format_strings, rows_to_write)
