import requests
import time

f = open('token.txt', 'r')
token = f.read()
#print(token)
f.close()

GroupId = '16915455'

request_params = {'token': token}
response_url = 'https://api.groupme.com/v3/groups/'+GroupId+'/messages'
message_ids = []


while True:
    messages = requests.get(response_url, params=request_params).json()['response']['messages']

    for message in messages:
        message_data = dict()
        allowed_fields = ['id', 'text', 'created_at', 'attachments', 'sender_id', 'favorited_by']
        if message['sender_type'] is not 'bot':
            if message['id'] not in message_ids:
                message_ids.append(message['id'])
                for x in allowed_fields:
                    message_data[x] = message[x]
            print(message_data)
    time.sleep(5)
