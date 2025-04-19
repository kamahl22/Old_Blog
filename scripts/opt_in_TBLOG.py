import os
from algosdk.v2client import algod
from algosdk import transaction, mnemonic, account
from dotenv import load_dotenv

load_dotenv()

def opt_in_tblog():
    client = algod.AlgodClient("", "https://testnet-api.4160.nodely.dev")
    
    bot_mnemonic = os.getenv("BOT_MNEMONIC")
    if not bot_mnemonic:
        raise ValueError("BOT_MNEMONIC not found in .env")
    bot_private_key = mnemonic.to_private_key(bot_mnemonic)
    bot_address = account.address_from_private_key(bot_private_key)
    asset_id = os.getenv("TBLOG_ASSET_ID")
    if not asset_id:
        raise ValueError("TBLOG_ASSET_ID not found in .env")

    params = client.suggested_params()
    txn = transaction.AssetOptInTxn(
        sender=bot_address,
        sp=params,
        index=int(asset_id)
    )
    signed_txn = txn.sign(bot_private_key)
    txid = client.send_transaction(signed_txn)
    transaction.wait_for_confirmation(client, txid, 4)
    print(f"Bot opted-in to TBLOG. TxID: {txid}")
    print(f"Verify: https://testnet.explorer.perawallet.app/address/{bot_address}")

if __name__ == "__main__":
    try:
        opt_in_tblog()
    except Exception as e:
        print(f"Error: {e}")