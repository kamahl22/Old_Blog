import os
from algosdk.v2client import algod
from algosdk import transaction, mnemonic, account
from dotenv import load_dotenv

load_dotenv()

def transfer_tblog_to_test():
    client = algod.AlgodClient("", "https://testnet-api.4160.nodely.dev")
    
    creator_mnemonic = os.getenv("CREATOR_MNEMONIC")
    if not creator_mnemonic:
        raise ValueError("CREATOR_MNEMONIC not found in .env")
    creator_private_key = mnemonic.to_private_key(creator_mnemonic)
    creator_address = account.address_from_private_key(creator_private_key)
    test_account_address = "O3UE7B5AE2FZR3CBWTDQFGHRLWHV2LAT26WPSOCLRBHWOAKEWHYL43HVLU"
    asset_id = os.getenv("TBLOG_ASSET_ID")
    if not asset_id:
        raise ValueError("TBLOG_ASSET_ID not found in .env")

    params = client.suggested_params()
    txn = transaction.AssetTransferTxn(
        sender=creator_address,
        sp=params,
        receiver=test_account_address,
        amt=100_000_000,  # 100 TBLOG (6 decimals)
        index=int(asset_id)
    )
    signed_txn = txn.sign(creator_private_key)
    txid = client.send_transaction(signed_txn)
    transaction.wait_for_confirmation(client, txid, 4)
    print(f"Transferred 10 TBLOG to test wallet. TxID: {txid}")
    print(f"Verify: https://testnet.explorer.perawallet.app/address/{test_account_address}")

if __name__ == "__main__":
    try:
        transfer_tblog_to_test()
    except Exception as e:
        print(f"Error: {e}")