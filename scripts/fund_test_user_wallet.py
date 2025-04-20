import os
from algosdk.v2client import algod
from algosdk import transaction, mnemonic, account
from dotenv import load_dotenv

load_dotenv()

def fund_test_wallet():
    client = algod.AlgodClient("", "https://testnet-api.4160.nodely.dev")
    
    creator_mnemonic = os.getenv("TEST_MNEMONIC")
    if not creator_mnemonic:
        raise ValueError("TEST_MNEMONIC not found in .env")
    creator_private_key = mnemonic.to_private_key(creator_mnemonic)
    creator_address = account.address_from_private_key(creator_private_key)
    test_address = "6Q4S5K7FJOBSU7S6UCC6XK4AQR6W2HA6XA7AE4KX3WJPIV74BAYYD6VVKY"

    params = client.suggested_params()
    txn = transaction.PaymentTxn(
        sender=creator_address,
        sp=params,
        receiver=test_address,
        amt=2_000_000  # 2 ALGO (in microALGO)
    )
    signed_txn = txn.sign(creator_private_key)
    txid = client.send_transaction(signed_txn)
    transaction.wait_for_confirmation(client, txid, 4)
    print(f"Transferred 2 ALGO to test wallet. TxID: {txid}")
    print(f"Verify: https://testnet.explorer.perawallet.app/address/{test_address}")

if __name__ == "__main__":
    try:
        fund_test_wallet()
    except Exception as e:
        print(f"Error: {e}")