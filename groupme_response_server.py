from flask import Flask, request, jsonify
from argparse import ArgumentParser
import chatbot_models

"""
Should this be in the main function????

Should this just be a flask app?????
"""

app = Flask(__name__)


@app.route('/get_response', methods=['POST'])
def send_message():
    """
    Expects a json in the form of {"Message": "Sentence goes here"}
    :return:
    """
    context = request.json
    user_message = context['Message']
    print(context['Message'])

    return jsonify({"ChatBotMessage": chatbot_models.respond(chat_bot, user_message)})


def setup():
    parser = ArgumentParser(description="run a server to check a file and write to a new one if there is a new message"
                                        "in the file waiting to get a response")
    parser.add_argument('-i', '--input-path', help='file to check for a new message')
    args = parser.parse_args()

    return chatbot_models.ChatBotModel(args.input_path)


if __name__ == '__main__':
    chat_bot = setup()

    app.run(host='0.0.0.0', debug=True)
