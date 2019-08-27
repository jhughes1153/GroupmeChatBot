import pymysql
import configparser
import logging

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
    logging.info(config[account])
    database_engines[name] = config[account]


def execute(name: str, sql: str) -> list:
    """This function not good for large queries"""
    logging.info(sql)

    output = None
    config = database_engines[name]
    connection = pymysql.connect(host=config['HOST'],
                                 user=config['USER'],
                                 password=config['PASSWORD'],
                                 db=config['DATABASE'],
                                 cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql)
            output = cursor.fetchall()
        connection.commit()
    except Exception as e:
        logging.error(e)
    finally:
        connection.close()

    return output
