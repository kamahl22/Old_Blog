import os
from algosdk.v2client import algod
from algosdk import transaction, mnemonic, account
from dotenv import load_dotenv

load_dotenv()

def create_tblog():
    client = algod.AlgodClient("", "https://testnet-api.4160.nodely.dev")
    
    creator_mnemonic = os.getenv("CREATOR_MNEMONIC")
    if not creator_mnemonic:
        raise ValueError("CREATOR_MNEMONIC not found in .env")
    creator_private_key = mnemonic.to_private_key(creator_mnemonic)
    creator_address = account.address_from_private_key(creator_private_key)
    
    bot_mnemonic = os.getenv("BOT_MNEMONIC")
    if not bot_mnemonic:
        raise ValueError("BOT_MNEMONIC not found in .env")
    bot_private_key = mnemonic.to_private_key(bot_mnemonic)
    bot_address = account.address_from_private_key(bot_private_key)

    sp = client.suggested_params()
    txn = transaction.AssetConfigTxn(
        sender=creator_address,
        sp=sp,
        default_frozen=False,
        unit_name="TBLOG",
        asset_name="BLOG Test Token",
        manager=bot_address,
        reserve=creator_address,
        freeze=bot_address,
        clawback=bot_address,
        url="https://github.com/kamahl22/Blog",
        total=1_000_000_000,
        decimals=6
    )
    
    stxn = txn.sign(creator_private_key)
    txid = client.send_transaction(stxn)
    print(f"Sent asset create transaction with txid: {txid}")
    results = transaction.wait_for_confirmation(client, txid, 4)
    print(f"Result confirmed in round: {results['confirmed-round']}")
    asset_id = results["asset-index"]
    print(f"TBLOG Asset ID: {asset_id}")
    print(f"Verify: https://testnet.explorer.perawallet.app/asset/{asset_id}")
    
    with open(".env", "a") as f:
        f.write(f"TBLOG_ASSET_ID={asset_id}\n")
    return asset_id

if __name__ == "__main__":
    try:
        create_tblog()
    except Exception as e:
        print(f"Error: {e}")