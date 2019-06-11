from groupy.client import Client

f = open('token.txt', 'r')


token = f.read()
print(token)
client = Client.from_token(token)

for group in client.groups.list_all():
    print(group.name)
