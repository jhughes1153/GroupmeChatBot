import asyncio
from argparse import ArgumentParser
import chatbot_models

"""
Should this be in the main function????

Should this just be a flask app?????
"""


class MessageHandler:
    def __init__(self, groupme_in, groupme_out):
        self.groupme_in = groupme_in
        self.groupme_out = groupme_out
        self.send_message = False


def get_current_groupme_message():
    print("Fuckin getting other messages")
    groupme_messages = ""
    return ""


def send_groupme_message(message, chatbot):
    print("Fucking sending other message")
    response = chatbot_models.respond(chatbot, message)
    print(response)
    # TODO send response


async def read_message(message_handler):
    while True:
        await asyncio.sleep(60)
        print("Reading message from file and checking if it did anything")
        # TODO add code here to get message from groupme
        message = get_current_groupme_message()  # grab messages from groupme
        if message_handler.check_in_change(message):
            message_handler.groupme_out = ""  # generate model message here
            print(message_handler.groupme_out)
            message_handler.send_message = True
        else:
            print("No updates waiting...")


async def send_message(message_handler, chatbot):
    while True:
        await asyncio.sleep(1)
        if message_handler.send_message:
            send_groupme_message()
        else:
            print("No new messages")


def main():
    parser = ArgumentParser(description="run a server to check a file and write to a new one if there is a new message"
                                        "in the file waiting to get a response")
    parser.add_argument('-i', '--input-path', help='file to check for a new message')
    parser.add_argument('-o', '--output-path', help='file to write out to if there is a new message')
    args = parser.parse_args()

    chatbot = chatbot_models.ChatBotModel(args.path)

    message_handler = MessageHandler("Initialize")
    loop = asyncio.get_event_loop()
    try:
        asyncio.ensure_future(read_message(message_handler))
        asyncio.ensure_future(send_message(message_handler, chatbot))
        # run forever until interrupted by user
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        print("Closing Loop")
        loop.close()


if __name__ == '__main__':
    main()
