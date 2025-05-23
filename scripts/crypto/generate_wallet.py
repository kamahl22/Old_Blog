from algosdk import account, mnemonic
def generate_wallet():
    private_key, address = account.generate_account()
    mnemonic_phrase = mnemonic.from_private_key(private_key)
    return {"address": address, "mnemonic": mnemonic_phrase}
if __name__ == "__main__":
    wallet = generate_wallet()
    print(f"Address: {wallet['address']}")
    print(f"Mnemonic: {wallet['mnemonic']}")
