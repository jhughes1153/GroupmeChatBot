import pandas as pd
import json
from argparse import ArgumentParser
import nltk
import string
import random
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

GREETING_INPUTS = ("hello", "hi", "greetings", "sup", "what's up", "hey",)
GREETING_RESPONSES = ["hi", "hey", "*nods*", "hi there", "hello", "I am glad! You are talking to me"]


class ChatBotModel:
    def __init__(self, file: str):
        self.lemmer = None
        self.sent_tokens = None
        self.parse_file(file)

    def parse_file(self, file: str):
        with open(file, 'r') as f:
            raw = f.read()
            print(f"Finished parsing {file}")

        raw = raw.lower()

        self.sent_tokens = nltk.sent_tokenize(raw)
        self.lemmer = nltk.stem.WordNetLemmatizer()

    def lem_tokens(self, tokens):
        return [self.lemmer.lemmatize(token) for token in tokens]

    def lem_normalize(self, text):
        remove_punct_dict = dict((ord(punct), None) for punct in string.punctuation)
        return self.lem_tokens(nltk.word_tokenize(text.lower().translate(remove_punct_dict)))

    def gen_response(self, user_response: str) -> str:
        robo_response = ''
        self.sent_tokens.append(user_response)
        tfidvec = TfidfVectorizer(tokenizer=self.lem_normalize, stop_words='english')
        tfidf = tfidvec.fit_transform(self.sent_tokens)
        vals = cosine_similarity(tfidf[-1], tfidf)
        idx = vals.argsort()[0][-2]
        flat = vals.flatten()
        flat.sort()
        req_tfidf = flat[-2]
        if req_tfidf == 0:
            robo_response = f"{robo_response} I'm sorry, I don't understand you"
            return robo_response
        else:
            robo_response = f"{robo_response} {self.sent_tokens[idx]}"
            return robo_response


def greeting(sentence: str):
    for word in sentence.split():
        if word.lower() in GREETING_INPUTS:
            return random.choice(GREETING_RESPONSES)


def respond(chat_bot_model: ChatBotModel, user_response: str) -> str:
    chatbot_response = chat_bot_model.gen_response(user_response)
    chat_bot_model.sent_tokens.remove(user_response)

    return chatbot_response


def test_model(chat_bot_model: ChatBotModel):
    print("ROBO: My name is Robo. I will answer your queries about Chatbots. If you want to exit, type Bye!")
    while True:
        user_response = input()
        user_response = user_response.lower()
        if user_response != 'bye':
            if user_response in ('thanks', 'thank you'):
                print("Fuck off ya wee bitch")
                break
            else:
                if greeting(user_response) is not None:
                    greet = greeting(user_response)
                    print(f"ROBO: {greet}")
                else:
                    print("ROBO:", end="")
                    print(chat_bot_model.gen_response(user_response))
                    chat_bot_model.sent_tokens.remove(user_response)
        else:
            print("ROBO: Bye! take care...")
            break


def create_model_readable(path: str, json_path: str):
    with open(json_path, 'r') as f:
        json_temp = json.load(f)

    df = pd.DataFrame(json_temp)

    with open(path, 'w') as f:
        for counter, row in df.iterrows():
            if row['text'] is None:
                print(f"Not adding {counter}")
            else:
                f.write('{}\n'.format(row['text']))


def main():
    parser = ArgumentParser(description="specify file to read from")
    parser.add_argument('-p', '--path', help="path to the text file to train on", required=True)
    parser.add_argument('-j', '--json-path', help="accepts a json file as input and creates a new txt file and keeps"
                                                  "that new file in the model, set the location to the path arguments")
    args = parser.parse_args()

    if args.json_path is not None:
        create_model_readable(args.path, args.json_path)

    chat_bot = ChatBotModel(args.path)

    test_model(chat_bot)


if __name__ == '__main__':
    main()
