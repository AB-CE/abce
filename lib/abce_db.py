""" must be imported with ' from agentengine import * ' by all agents """
import zmq
import multiprocessing
from abce_common import agent_name, group_address
import MySQLdb as mdb


class DbAgent(multiprocessing.Process):
    """ must be inherited by all agents as first line in def ' __init__(self)':
    (see agent.py prototype)
    """
    def __init__(self, simulation_name, group, command):
        multiprocessing.Process.__init__(self)
        self.db_connection = mdb.connect('localhost', 'abce', 'ictilo', simulation_name);
        self.command = command
        self.table_name = command + '_' + group
        self.group = group
        self.round = 0

    def run(self):
        """ internal """
        context = zmq.Context()
        self.in_sok = context.socket(zmq.SUB)
        self.in_sok.connect("ipc://backend.ipc")
        self.in_sok.setsockopt(zmq.SUBSCRIBE, "db_agent:" + self.command + ":" + self.group)
        self.in_sok.setsockopt(zmq.SUBSCRIBE, "db_agent:close")
        self.in_sok.setsockopt(zmq.SUBSCRIBE, "db_agent:advance_round")
        begin = "INSERT INTO " + self.table_name + "(round, id,"
        values = ") VALUES (%s)"
        with self.db_connection:
            cursor = self.db_connection.cursor()
            ex_str = "CREATE TABLE " + self.table_name + "(round INT, id INT)"
            cursor.execute(ex_str)

        while True:
            address_command = self.in_sok.recv()
            if address_command == "db_agent:close":
                break
            if address_command == "db_agent:advance_round":
                self.round += 1
                continue
            idn = int(self.in_sok.recv())
            data_to_write = self.in_sok.recv_json()
            data_to_write['round'] = self.round
            data_to_write['id'] = idn
            write(self.db_connection, self.table_name, data_to_write)


class DbFollowAgent(multiprocessing.Process):
    """ must be inherited by all agents as first line in def ' __init__(self)':
    (see agent.py prototype)
    """
    def __init__(self, simulation_name):
        multiprocessing.Process.__init__(self)
        self.db_connection = mdb.connect('localhost', 'abce', 'ictilo', simulation_name);
        self.round = 0
        self.follow_agent_list = []

    def add(self, group, number):
        with self.db_connection:
            cursor = self.db_connection.cursor()
            ex_str = "CREATE TABLE " + group + '_' + str(number) + "(round INT, command CHAR(20), name CHAR(20))"
            cursor.execute(ex_str)
            self.follow_agent_list.append("db_agent:" + group_address(group))

    def run(self):
        """ internal """
        context = zmq.Context()
        self.in_sok = context.socket(zmq.SUB)
        self.in_sok.connect("ipc://backend.ipc")
        for sub in self.follow_agent_list:
            self.in_sok.setsockopt(zmq.SUBSCRIBE, sub)
        self.in_sok.setsockopt(zmq.SUBSCRIBE, "db_agent:close")
        self.in_sok.setsockopt(zmq.SUBSCRIBE, "db_agent:advance_round")
        while True:
            address_command = self.in_sok.recv()
            if address_command == "db_agent:close":
                break
            if address_command == "db_agent:advance_round":
                self.round += 1
                continue
            name = self.in_sok.recv()[0:-1]
            command = self.in_sok.recv()
            data_to_write = self.in_sok.recv_json()
            data_to_write['name'] = name
            data_to_write['command'] = command
            data_to_write['round'] = self.round
            write(self.db_connection, name, data_to_write)

def write(db_connection, table_name, data_to_write):
    values = ") VALUES (%s)"
    with db_connection:
        cursor = db_connection.cursor()
        rows_to_write = (data_to_write.values())
        format_strings = ','.join(['%s'] * len(rows_to_write))
        begin = "INSERT INTO " + table_name + "("
        ex_str = begin + ','.join(data_to_write.keys()) + values
        try:
            cursor.execute(ex_str % format_strings, rows_to_write)
        except (TypeError, mdb.OperationalError):
            for key in data_to_write:
                cursor.execute(""" SHOW columns FROM """ + table_name)
                existing_columns = [row[0] for row in cursor]
                new_columns = set(data_to_write.keys()).difference(existing_columns)
                for column in new_columns:
                    cursor.execute(""" ALTER TABLE """ + table_name + """ ADD """ + column + """ FLOAT;""")
            format_strings = ','.join(['%s'] * len(rows_to_write))
            cursor.execute(ex_str % format_strings, rows_to_write)


def create_database(simulation_name):
    db_connection = mdb.connect('localhost', 'abce', 'ictilo');
    with db_connection:
        cursor = db_connection.cursor()
        suffix = ''
        while cursor.execute(
                "SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = '"
                + simulation_name + suffix + "'"):
            if not(suffix):
                suffix = 'a'
            else:
                suffix = chr(ord(suffix) + 1)
        ex_str = "CREATE DATABASE " + simulation_name + suffix
        cursor.execute(ex_str)
    return simulation_name + suffix