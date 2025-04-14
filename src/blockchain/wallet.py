# src/blockchain/wallet.py
from algosdk import account, mnemonic

class AlgorandWallet:
    def __init__(self):
        self.private_key, self.address = account.generate_account()
        self.mnemonic = mnemonic.from_private_key(self.private_key)

    def get_details(self):
        return {
            "address": self.address,
            "mnemonic": self.mnemonic,
            "private_key": self.private_key
        }

    @staticmethod
    def from_mnemonic(mnemonic_phrase):
        wallet = AlgorandWallet()
        wallet.private_key = mnemonic.to_private_key(mnemonic_phrase)
        wallet.address = account.address_from_private_key(wallet.private_key)
        wallet.mnemonic = mnemonic_phrase
        return wallet

if __name__ == "__main__":
    wallet = AlgorandWallet()
    details = wallet.get_details()
    print(f"Address: {details['address']}")
    print(f"Mnemonic: {details['mnemonic']}")