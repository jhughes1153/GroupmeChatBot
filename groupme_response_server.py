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


class MostRecentStruct:
    def __init__(self, id_, message):
        self.id_ = id_
        self.messages = message


async def read_message(response_url, request_params, most_recent_struct):
    while True:
        await asyncio.sleep(60)
        messages = requests.get(response_url, params=request_params).json()['response']['messages']
        most_recent_struct.message = messages[0]['text']
        most_recent_struct.id_ = messages[0]['id']


async def send_message(most_recent_struct, chatbot):
    while True:
        await asyncio.sleep(5)
        


def main():
    parser = ArgumentParser(description='Runs the server for the groupmechatbot')
    parser.add_argument('-t', '--token', help='Groupme token', required=True)
    parser.add_argument('-a', '--account', help='Database account to access')
    parser.add_argument('-i', '--model-input-file', help='txt file for the model')
    args = parser.parse_args()

    request_params = {'token': args.token}
    response_url = 'https://api.groupme.com/v3/groups/16915455/messages'

    chatbot = chatbot_models.ChatBotModel(args.model_input_file)
    most_recent_struct = MostRecentStruct('', '')

    loop = asyncio.get_event_loop()

    try:
        asyncio.ensure_future(read_message(request_params, response_url, most_recent_struct))
        asyncio.ensure_future(send_message(most_recent_struct, chatbot))

        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        print('Closing loop')
        loop.close()


if __name__ == '__main__':
    main()
