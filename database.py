import pymysql
import configparser

database_engines = {}


def init_database(name, account, config_file):
    config = configparser.ConfigParser().read(config_file)
    with pymysql.connect(
        host=config[account]['HOST'],
        user=config[account]['USER'],
        password=config[account]['PASS'],
        db='groupmebot'
    ) as conn:
        database_engines[name] = conn.cursor()


def execute(name, sql):
    """This function not good for large queries"""
    output = database_engines[name].execute(sql).fetchall()
    database_engines[name].commit()
    return output


def close(name):
    database_engines[name].close()

