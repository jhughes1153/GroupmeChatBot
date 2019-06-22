import pymysql
import configparser

"""
Usage:
    
    database.init_database('db', 'DEFAULT', '/home/jackh/config.ini')
    
    then at anytime after that just call:
    output = database.execute('db', 'SELECT * FROM FOO')
"""


database_engines = {}


def init_database(name: str, account: str, config_file: str):
    config = configparser.ConfigParser()
    config.read(config_file)
    connection = pymysql.connect(
        host=config[account]['HOST'],
        user=config[account]['USER'],
        password=config[account]['PASSWORD'],
        db=config[account]['DATABASE'],
        cursorclass=pymysql.cursors.DictCursor
    )
    database_engines[name] = connection


def execute(name: str, sql: str) -> list:
    """This function not good for large queries"""
    with database_engines[name].cursor() as cursor:
        cursor.execute(sql)
        output = cursor.fetchall()
        print(output)
        database_engines[name].commit()
    return output
