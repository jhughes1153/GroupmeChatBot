import requests
from argparse import ArgumentParser
import chatbot_models
import asyncio
import database
from logger import LoggingEnv
import logging
import pandas as pd

"""
Main server, makes requests and send messages to chatbot

Lets worry about database connectivity after we already have this up and running
as it currently takes a static file, but ChatBotModel can take a file at any
time so we can add that later
"""

db_mappings = {'id': 'ID', 'created_at': 'CREATED_AT', 'name': 'NAME', 'text': 'MESSAGE', 'user_id': 'USER_ID'}

class MostRecentId:
    def __init__(self, unique_id, message):
        self.unique_id = unique_id
        self.message = message

    def verify(self, message):
        if message == self.message:
            return False
        return True


class RequestHelper:
    def __init__(self, url, request_params, post_params):
        self.url = url
        self.request_params = request_params
        self.post_params = post_params
        self.startup_state = True


async def read_message(request_helper, most_recent, chatbot):
    print("reading messages")
    count = 10
    while True:
        try:
            request = requests.get(request_helper.url, params=request_helper.request_params)
        except Exception as e:
            logging.info(e)
            logging.info("Waiting 10 minutes before next run")
            await asyncio.sleep(600)
            count += 1
            if count == 10:
                raise KeyboardInterrupt

        logging.info(request.status_code)
        if request.status_code != 200:
            logging.error('Failed to get anything skipping I guess')
        else:
            messages = request.json()['response']['messages']
            messages.reverse()
            logging.info(most_recent.unique_id)
            if request_helper.startup_state:
                logging.info("Initial startup running skipping first iteration")
                request_helper.startup_state = False
                await asyncio.sleep(120)
                continue
            else:
                for m in messages:
                    if m['created_at'] > most_recent.unique_id and most_recent.verify(m['text']) and m['name'] != 'Annoyance101':
                        logging.info(m['text'])
                        most_recent.unique_id = m['created_at']
                        most_recent.message = m['text']
                        if m['text'] is None:
                            continue
                        append_database(m['id'], m['created_at'], m['name'], m['text'], m['user_id'])
                        if '@bot' in m['text']:
                            print(m['text'])
                            logging.info('Appending database')
                            send_message(chatbot, m['text'], request_helper)
        await asyncio.sleep(120)


def append_database(id_, created_at, name, message, sender):
    logging.info(f'Appending message: {created_at}')
    logging.info(f'Messages: {message}, sender: {sender}')
    message = message.replace("'", '').replace('"', '')
    name = name.replace("'", '').replace('"', '')
    try:
        database.execute('groupmebot', f"INSERT INTO GROUPMEBOT.MESSAGES VALUES('{id_}', {created_at}, '{name}', '{message}', "
                                       f"{sender})")
    except Exception as e:
        logging.error(e)
        logging.error('Failed to upload to database')


def send_message(chatbot: chatbot_models.ChatBotModel, message: str, request_helper: RequestHelper) -> None:
    message = message.replace(' @bot', '')
    logging.info(message)
    response = str(chatbot_models.respond(chatbot, message)).split('\n')[0]
    logging.info(type(response))
    logging.info(response)
    request_helper.post_params['text'] = response
    logging.info("Printing what is inside of the dictionary")
    logging.info(request_helper.post_params)
    # hardcoded to be annoyancebot right now
    logging.info("sending messages")
    requests.post('https://api.groupme.com/v3/bots/post', params=request_helper.post_params)


def init_most_recent(most_recent):
    most_recent.unique_id = database.execute('groupmebot', 'SELECT MAX(CREATED_AT) FROM '
                                                           'GROUPMEBOT.MESSAGES')[0]['MAX(CREATED_AT)']


def init_model(database, model_input_file):
    df = pd.DataFrame(database.execute('groupmebot', "SELECT * FROM GROUPMEBOT.MESSAGES"))
    df.to_json("/tmp/temp_file.json", orient='records')
    chatbot_models.create_model_readable_from_file(model_input_file, '/tmp/temp_file.json')

    return chatbot_models.ChatBotModel(model_input_file)


def main():
    parser = ArgumentParser(description='Runs the server for the groupmechatbot')
    parser.add_argument('-t', '--token', help='Groupme token', default='VArZCH69ta1GSoq1uK13k80Zhu0OJi5czkz93099')
    parser.add_argument('-a', '--account', help='Database account to access')
    parser.add_argument('-i', '--model-input-file', help='txt file for the model')
    parser.add_argument('-b', '--bot-id', help='bot id to use for groupme response',
                        default='4a38538df10cf8273ed53752bc')
    parser.add_argument('-c', '--config-path', help='path to the db config file', required=True)
    args = parser.parse_args()

    LoggingEnv("GroupmeChatBot")

    request_params = {'token': args.token}
    post_params = {'bot_id': args.bot_id, 'text': 'Testing'}
    response_url = 'https://api.groupme.com/v3/groups/16915455/messages'

    request_helper = RequestHelper(response_url, request_params, post_params)

    database.init_database('groupmebot', args.account, args.config_path)

    chatbot = init_model(database, args.model_input_file)
    most_recent = MostRecentId(0, '')

    init_most_recent(most_recent)

    loop = asyncio.get_event_loop()

    try:
        asyncio.ensure_future(read_message(request_helper, most_recent, chatbot))
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        logging.info('Closing loop')
        loop.close()
        request_helper.post_params['text'] = 'Crashing gracefully'
        requests.post('https://api.groupme.com/v3/bots/post', params=request_helper.post_params)


if __name__ == '__main__':
    main()
