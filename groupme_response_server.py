import requests
from argparse import ArgumentParser
import chatbot_models
import asyncio

"""
Main server, makes requests and send messages to chatbot

Lets worry about database connectivity after we already have this up and running
as it currently takes a static file, but ChatBotModel can take a file at any
time so we can add that later
"""


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
        await asyncio.sleep(60)
        messages = requests.get(request_helper, params=request_helper.request_params).json()['response']['messages']
        for m in messages:
            if m['id'] > most_recent.unique_id:
                append_database(m['id'], m['text'], m['sender_id '])
                most_recent.unique_id = m['id']
                if '@bot' in m['text']:
                    send_message(chatbot, m['text'], request_helper)


def append_database(id_, message, sender):
    print(id_, message, sender)


def send_message(chatbot: chatbot_models.ChatBotModel, message: str, request_helper: RequestHelper) -> None:
    message = message.split('@bot')[0]
    chatbot_models.respond(chatbot, message)
    # hardcoded to be annoyancebot right now
    requests.post('https://api.groupme/v3/bots/post', request_helper.post_params)


def main():
    parser = ArgumentParser(description='Runs the server for the groupmechatbot')
    parser.add_argument('-t', '--token', help='Groupme token', required=True)
    parser.add_argument('-a', '--account', help='Database account to access')
    parser.add_argument('-i', '--model-input-file', help='txt file for the model')
    parser.add_argument('-b', '--bot-id', help='bot id to use for groupme response', required=True)
    args = parser.parse_args()

    request_params = {'token': args.token}
    post_params = {'bot_id': args.bot_id}
    response_url = 'https://api.groupme.com/v3/groups/16915455/messages'

    request_helper = RequestHelper(response_url, request_params, post_params)

    chatbot = chatbot_models.ChatBotModel(args.model_input_file)
    most_recent = MostRecentId(0)

    loop = asyncio.get_event_loop()

    try:
        asyncio.ensure_future(read_message(request_helper, most_recent, chatbot))
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        print('Closing loop')
        loop.close()


if __name__ == '__main__':
    main()
