import requests
from argparse import ArgumentParser
import chatbot_models
import asyncio
import database

"""
Main server, makes requests and send messages to chatbot

Lets worry about database connectivity after we already have this up and running
as it currently takes a static file, but ChatBotModel can take a file at any
time so we can add that later
"""

db_mappings = {'id': 'ID', 'created_at': 'CREATED_AT', 'name': 'NAME', 'text': 'MESSAGE', 'user_id': 'USER_ID'}


class MostRecentId:
    def __init__(self, unique_id):
        self.unique_id = unique_id


class RequestHelper:
    def __init__(self, url, request_params, post_params):
        self.url = url
        self.request_params = request_params
        self.post_params = post_params


async def read_message(request_helper, most_recent, chatbot):
    while True:
        await asyncio.sleep(120)
        print(request_helper.url)
        print(request_helper.request_params)
        request = requests.get(request_helper.url, params=request_helper.request_params)
        print(request.url)
        print(request.status_code)
        if request.status_code != 200:
            print('Failed to get anything skipping I guess')
        else:
            messages = request.json()['response']['messages']
            print(most_recent.unique_id)
            for m in messages:
                if m['created_at'] > most_recent.unique_id:
                    most_recent.unique_id = m['created_at']
                    if m['text'] is None:
                        continue
                    print(m)
                    append_database(m['id'], m['created_at'], m['name'], m['text'], m['user_id'])
                    if '@bot' in m['text']:
                        print('Appending database')
                        send_message(chatbot, m['text'], request_helper)


def append_database(id_, created_at, name, message, sender):
    message = message.replace("'", '').replace('"', '')
    name = name.replace("'", '').replace('"', '')
    database.execute('groupmebot', f"INSERT INTO GROUPMEBOT.MESSAGES VALUES('{id_}', {created_at}, '{name}', '{message}', "
                                   f"{sender})")


def send_message(chatbot: chatbot_models.ChatBotModel, message: str, request_helper: RequestHelper) -> None:
    message = message.replace(' @bot', '')
    print(message)
    response = str(chatbot_models.respond(chatbot, message))
    print(type(response))
    print(response)
    request_helper.post_params['text'] = response
    print("Printing what is inside of the dictionary")
    print(request_helper.post_params)
    # hardcoded to be annoyancebot right now
    print("sending messages")
    requests.post('https://api.groupme.com/v3/bots/post', params=request_helper.post_params)


def init_most_recent(most_recent):
    most_recent.unique_id = database.execute('groupmebot', 'SELECT MAX(CREATED_AT) FROM '
                                                           'GROUPMEBOT.MESSAGES')[0]['MAX(CREATED_AT)']


def main():
    parser = ArgumentParser(description='Runs the server for the groupmechatbot')
    parser.add_argument('-t', '--token', help='Groupme token', default='VArZCH69ta1GSoq1uK13k80Zhu0OJi5czkz93099')
    parser.add_argument('-a', '--account', help='Database account to access')
    parser.add_argument('-i', '--model-input-file', help='txt file for the model')
    parser.add_argument('-b', '--bot-id', help='bot id to use for groupme response',
                        default='4a38538df10cf8273ed53752bc')
    parser.add_argument('-c', '--config-path', help='path to the db config file', required=True)
    args = parser.parse_args()

    request_params = {'token': args.token}
    post_params = {'bot_id': args.bot_id, 'text': 'Testing for fucks sake'}
    response_url = 'https://api.groupme.com/v3/groups/16915455/messages'

    request_helper = RequestHelper(response_url, request_params, post_params)

    chatbot = chatbot_models.ChatBotModel(args.model_input_file)
    most_recent = MostRecentId(0)

    database.init_database('groupmebot', args.account, args.config_path)
    init_most_recent(most_recent)

    loop = asyncio.get_event_loop()

    try:
        asyncio.ensure_future(read_message(request_helper, most_recent, chatbot))
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        print('Closing loop')
        loop.close()
        send_message(chatbot, 'Crashing', request_helper)


if __name__ == '__main__':
    main()
