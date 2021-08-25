import mysql.connector
import time
import os
import digimon

connections = {}


def connect(host, database, username, password):
    connections['main'] = mysql.connector.connect(
        host=host,
        user=username,
        passwd=password,
        database=database
    )
    print('MySQL connected')


def get_connection(name='main'):
    return connections[name].cursor(dictionary=True)


def commit(name='main'):
    connections[name].commit()

