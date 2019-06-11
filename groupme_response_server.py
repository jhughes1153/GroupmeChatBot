import chatbot_models
from argparse import ArgumentParser


def main():
    parser = ArgumentParser(description="specify file to read from")
    parser.add_argument('-p', '--path', help="path to the text file to train on", required=True)
    args = parser.parse_args()

    chat_bot = chatbot_models.ChatBotModel(args.path)

    # TODO code here to run inifitely waiting for responses from groupme?


if __name__ == '__main__':
    main()