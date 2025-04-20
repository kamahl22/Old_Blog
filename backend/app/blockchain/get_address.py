import os
from algosdk import mnemonic, account
from dotenv import load_dotenv

load_dotenv()

def get_address():
    mnemonic_phrase = os.getenv("CREATOR_MNEMONIC")
    if not mnemonic_phrase:
        raise ValueError("CREATOR_MNEMONIC not found in .env")
    private_key = mnemonic.to_private_key(mnemonic_phrase)
    address = account.address_from_private_key(private_key)
    print(f"Creator Address: {address}")

if __name__ == "__main__":
    try:
        get_address()
    except Exception as e:
        print(f"Error: {e}")