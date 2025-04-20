import os
from algosdk.v2client import algod
from algosdk import transaction, mnemonic, account
from dotenv import load_dotenv

load_dotenv()

def opt_in_test():
    client = algod.AlgodClient("", "https://testnet-api.4160.nodely.dev")
    
    test_mnemonic = os.getenv("TEST_MNEMONIC")
    if not test_mnemonic:
        raise ValueError("TTEST_MNEMONIC not found in .env")
    test_private_key = mnemonic.to_private_key(test_mnemonic)
    test_address = account.address_from_private_key(test_private_key)
    if test_address != "O3UE7B5AE2FZR3CBWTDQFGHRLWHV2LAT26WPSOCLRBHWOAKEWHYL43HVLU":
        raise ValueError("Mnemonic does not match test address O3UE7B5AE2FZR3CBWTDQFGHRLWHV2LAT26WPSOCLRBHWOAKEWHYL43HVLU")
    asset_id = os.getenv("TBLOG_ASSET_ID")
    if not asset_id:
        raise ValueError("TBLOG_ASSET_ID not found in .env")

    params = client.suggested_params()
    txn = transaction.AssetOptInTxn(
        sender=test_address,
        sp=params,
        index=int(asset_id)
    )
    signed_txn = txn.sign(test_private_key)
    txid = client.send_transaction(signed_txn)
    transaction.wait_for_confirmation(client, txid, 4)
    print(f"Test wallet opted-in to TBLOG. TxID: {txid}")
    print(f"Verify: https://testnet.explorer.perawallet.app/address/O3UE7B5AE2FZR3CBWTDQFGHRLWHV2LAT26WPSOCLRBHWOAKEWHYL43HVLU")

if __name__ == "__main__":
    try:
        opt_in_test()
    except Exception as e:
        print(f"Error: {e}")