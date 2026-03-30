# addusers.py
# Supports both CLI input and frontend (list passed directly)

def add(wallets=None):
    """
    CLI mode:   add()              → prompts user to type wallets
    Frontend:   add(["0x...", "0x..."]) → uses list directly
    """
    user_wallet = set()

    if wallets is not None:
        # called from frontend / api.py — wallets already provided
        for w in wallets:
            w = w.strip()
            if w:
                user_wallet.add(w)
        return user_wallet

    # CLI mode — original terminal behavior unchanged
    user_input = input("Add user's proxy wallet and press enter. Type x or X when done: ")
    while user_input.lower() != 'x':
        user_wallet.add(user_input.strip())
        user_input = input()

    return user_wallet