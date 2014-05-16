try:
    import sqlite3
    from sqlite3 import * #pylint: disable=W0614


    class CustomConnect:
        def __init__(self, directory, db_name):
            self.db = sqlite3.connect(directory + '/' + db_name + '.db')
            self.cursor = self.db.cursor()

        def execute(self, command):
            self.cursor.execute(command)
            self.description = self.cursor.description

        def executeQuery(self, command):
            return self.cursor.execute(command)

        def column_names(self, table_name):
            self.cursor.execute("""PRAGMA table_info(""" + table_name + """)""")
            return [row[1] for row in self.cursor]

        def table_ids(self, table_name):
            self.cursor.execute("""PRAGMA table_info(""" + table_name + """)""")
            return [row[0] for row in self.cursor]

        def fetchall(self):
            return self.cursor.fetchall()

        def fetchone(self):
            return self.cursor.fetchone()

        def commit(self):
            self.db.commit()

        def close(self):
            self.db.close()

    class SQLException(Exception):
        pass



except ImportError:
    import java.sql.SQLException as SQLException #pylint: disable=F0401
    import org.sqlite.SQLiteDataSource as SQLiteDataSource #pylint: disable=F0401


    class CustomConnect:
        def __init__(self, directory, db_name):
            dataSource = SQLiteDataSource()
            dataSource.setUrl("jdbc:sqlite:" + directory + '/' + db_name + '.db')
            self.connection = dataSource.getConnection()
            self.cursor = self.connection.createStatement()
            self.describtion = self.db.describtion

        def execute(self, command):
            self.cursor.execute(command)

        def executeQuery(self, command):
            return self.cursor.executeQuery(command)

        def column_names(self, table_name):
            table_info = self.cursor.executeQuery("""PRAGMA table_info(""" + table_name + """)""")
            columns = []
            while True:
                columns.append(table_info.getString(2))
                if not(table_info.next()):
                    break
            return columns

        def table_ids(self, table_name):
            table_info = self.cursor.executeQuery("""PRAGMA table_info(""" + table_name + """)""")
            columns = []
            while True:
                columns.append(table_info.getString(1))
                if not(table_info.next()):
                    break
            return columns

        def fetchall(self):
            return self.cursor.fetchall()

        def fetchone(self):
            return self.cursor.fetchone()

        def commit(self):
            try:
                self.connection.commit()
            except SQLException:
                if self.connection.getAutoCommit() == False:
                    raise

        def close(self):
            self.connection.close()

    class OperationalError(Exception):
        pass

    class InterfaceError(Exception):
        pass
