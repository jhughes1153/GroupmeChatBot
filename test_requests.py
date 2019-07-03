import mysql.connector
import requests
import time
import configparser
import argparse
import os
#import json

parser = argparse.ArgumentParser()

parser.add_argument("--token", help="add groupme token")
parser.add_argument("--host", help="add sql hostname")
parser.add_argument("--user", help="add sql username")
parser.add_argument("--password", help="add sql password")

args = parser.parse_args()

if args.token is None:
    f = open('token.txt', 'r')
    token = f.read()
    # print(token)
    f.close()
    if not token:
        exit(-1)
else:
    token = args.token

if args.host is None or args.user is None or args.password is None:
    if os.path.exists('config.ini'):
        config = configparser.ConfigParser()
        config.read('config.ini')

        mydb = mysql.connector.connect(
            host=config['DEFAULT']['HOST'],
            user=config['DEFAULT']['USER'],
            passwd=config['DEFAULT']['PASS'],
            database="groupmebot"
        )
    else:
        exit(-1)
else:
    mydb = mysql.connector.connect(
        host=args.host,
        user=args.user,
        passwd=args.password,
        database="groupmebot"
    )



'''
# SQL SETUP #


cursor = mydb.cursor()

#Accessing group#
f = open('token.txt', 'r')
token = f.read()
#print(token)
f.close()
'''
GroupId = '16915455'

request_params = {'token': token}
response_url = 'https://api.groupme.com/v3/groups/'+GroupId+'/messages'
message_ids = []


#i=0
#while i<1:
while True:
    messages = requests.get(response_url, params=request_params).json()['response']['messages']
    #print(messages)
    for message in messages:
        message_data = dict()
        allowed_fields = ['text', 'created_at', 'sender_id']
        if message['sender_type'] is not 'bot':
            cursor = mydb.cursor(buffered=True)
            sql = "SELECT * FROM messages WHERE created_at="+str(message['created_at'])
            result = cursor.execute(sql)
            if cursor.rowcount is 0:
                sql = 'INSERT INTO messages ('
                cursor.close()
                cursor = mydb.cursor(buffered=True)
                fields = ''
                values = ''
                for x in allowed_fields:

                    value = str(message[x]).replace("'", "")

                    if allowed_fields[len(allowed_fields)-1] is not x:
                        fields += x + ', '
                        values += value + '", "'
                    else:
                        fields += x + ')'
                        values += value + '")'
                sql += fields + ' VALUES ("' + values
                cursor.execute(sql)
                mydb.commit()
            cursor.close()
    #i=1
    time.sleep(5)


