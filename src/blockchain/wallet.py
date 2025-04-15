from algosdk import account, mnemonic
import os

class AlgorandWallet:
    def __init__(self, mnemonic_phrase=None):
        if mnemonic_phrase:
            self.private_key = mnemonic.to_private_key(mnemonic_phrase)
            self.address = account.address_from_private_key(self.private_key)
        else:
            self.private_key, self.address = account.generate_account()

    def get_details(self):
        return {
            "address": self.address,
            "mnemonic": mnemonic.from_private_key(self.private_key)
        }