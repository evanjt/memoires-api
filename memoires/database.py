#!/usr/bin/env python3

# Class and functions related to memoire storage in sqlite3

import sqlite3

class DBConnection:
    def __init__(self, filename):
        self.filename = filename

    def create_connection(self):
        ''' Isolation_level allows autocommit after each query.
            Function also creates the connection object in the class
        '''
        conn = None
        try:
            self.conn = sqlite3.connect(self.filename, isolation_level=None)
        except sqlite3.Error as e:
            print(e)
        #print("Connected to", self.filename)

    def drop_connection(self):
        self.conn.close()
        #print("Disconnected from", self.filename)

    def create_table(self, create_table_sql):
        """ create a table from the create_table_sql statement
        :param conn: Connection object
        :param create_table_sql: a CREATE TABLE statement
        :return:
        """
        try:
            c = self.conn.cursor()
            c.execute(create_table_sql)
        except sqlite3.Error as e:
            print(e)

    def initialise_tables(self):
      ## Create:
      # keywords table
      # people involved table
        table_list = [""" CREATE TABLE IF NOT EXISTS persons (
                            id integer PRIMARY KEY,
                            nickname text NOT NULL,
                            firstname text,
                            lastname text,
                            dob text,
                            nationality text,
                            met_on text,
                            last_known text,
                            notes text
                        ); """,
                      """ CREATE TABLE IF NOT EXISTS locations (
                            id integer PRIMARY KEY,
                            name text NOT NULL,
                            street text,
                            suburb text,
                            city text,
                            state text,
                            country text,
                            region text,
                            latitude text,
                            longitude text,
                            notes text
                        ); """,
                      """ CREATE TABLE IF NOT EXISTS events (
                            id integer PRIMARY KEY,
                            date text NOT NULL,
                            people_involved integer,
                            location integer,
                            keywords integer,
                            photo_id integer,
                            story text,
                            FOREIGN KEY (location) REFERENCES locations(id)
                        ); """,
                     """ CREATE TABLE IF NOT EXISTS events_attended (
                            id integer PRIMARY KEY,
                            personid integer NOT NULL,
                            eventid integer NOT NULL,
                            FOREIGN KEY (personid) REFERENCES persons(id),
                            FOREIGN KEY (eventid) REFERENCES events(id)
                        ); """,
                     """ CREATE TABLE IF NOT EXISTS blackbox (
                            id integer PRIMARY KEY,
                            story text NOT NULL
                        ); """]
        try:
            self.create_connection()
            count = 0
            for table in table_list:
                self.create_table(table)
                count += 1

            print("Initialised {} tables correctly".format(count))
            self.drop_connection()
        except sqlite3.Error:
            print("Error in initialising tables")
        print()

    def insert_blackbox(self, story):
        sql = """ INSERT INTO blackbox(story)
                    VALUES(?) """
        try:
            self.create_connection()
            self.conn.cursor().execute(sql, (story,))
            self.drop_connection()
            print("Inserted story into the blackbox")
        except sqlite3.Error:
                print("Error!")

    def fetch_blackbox(self):
        sql = """ SELECT * FROM blackbox """
        try:
            self.create_connection()
            cur = self.conn.cursor()
            cur.execute(sql)
            rows = cur.fetchall()
            self.drop_connection()
            for row in rows:
                print("{}: {}".format(row[0],row[1]))
        except:
            print("Error in returning rows from blackbox")
