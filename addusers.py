#addusers.py
def add():
    user_wallet = set()
    user_input=input("Add user's proxy wallet and press enter. Type x or X when done")
    while user_input.lower() != 'x':
        user_wallet.add(user_input)
        user_input=input()
    return user_wallet