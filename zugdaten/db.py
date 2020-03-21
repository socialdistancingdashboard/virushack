#!/home/bemootzer/anaconda3/envs/bahnfail/bin/python
"""Module handles connections to MySQL databases"""

import mysql.connector 
from mysql.connector import MySQLConnection, Error
import datetime


class DatabaseWrapper():
    """ Handles everything related to the database. """

    class Timer():
        """Measures time that passes for each action."""

        def __init__(self, verbose=True):
            self.verbose = verbose
            self._start = datetime.datetime.now()

        def stop(self):
            if self.verbose:
                print("duration:", datetime.datetime.now() - self._start)
        

    def __init__(self, host, database, user, password):
        self.config = {'host': host, 'database': database, 'user': user, 'password': password}
        self.test()

    def test(self):
        """ Tests the configuration. """
        print("testing database connection...")
        try:
            print('--> Connecting to MySQL database with (%s, %s, %s, %s)' % 
                (self.config['host'], 
                self.config['user'], 
                self.config['password'], 
                self.config['database']))

            conn = MySQLConnection(**self.config)
            if conn.is_connected():
                print('--> connection established.')
            else:
                print('--> connection failed.')
        except Error as error:
            print(error)
        finally:
            conn.close()
            print('Connection closed.\nTest passed.')

    def execute(self, query, rows_per_run=1000, verbose=False, multi=False):
        """ executes any query on database """
        timer = self.Timer(verbose=verbose)
        try:
            conn = MySQLConnection(**self.config)
            cursor = conn.cursor()
            cursor.execute(query, None, multi=multi)
        
            results = []
            while True:
                tmp = cursor.fetchmany(rows_per_run)
                if tmp:
                    results.extend(tmp)
                else:
                    break

            conn.commit()
            timer.stop()
            return results
        except Error as error:
            print(error)
        finally:
            cursor.close()
            conn.close()
       
    
    def execute_many(self, statement, data, line=None):
        """ fast way to insert much data. """
        timer = self.Timer()
        try:
            conn = MySQLConnection(**self.config)
            cursor = conn.cursor()
            cursor.executemany(statement, data)
            conn.commit()
            timer.stop()
        except Error as error:
            print(line, error)
        finally:
            cursor.close()
            conn.close()

def print_query(rows):
    if rows is None:
        return
    for row in rows:
        print(row)