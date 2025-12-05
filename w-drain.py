import os
import time
import requests
from tronpy import Tron
from tronpy.keys import PrivateKey
from dotenv import load_dotenv

load_dotenv()
SCAMMER_PRIVATE_KEY = os.getenv("SCAMMER_PRIVATE_KEY")
YOUR_WALLET_ADDRESS = os.getenv("YOUR_WALLET_ADDRESS")
API_KEY = os.getenv("API_KEY")

client = Tron()
scammer_priv_key = PrivateKey(bytes.fromhex(SCAMMER_PRIVATE_KEY))
scammer_address = scammer_priv_key.public_key.to_base58check_address()


def get_trx_balance(address):
    try:
        balance = client.get_account_balance(address)
        return balance
    except Exception as e:
        print("Gagal ambil TRX balance:", e)
        return 0

def get_usdt_balance(address):
    url = f"https://api.trongrid.io/v1/accounts/{address}"
    headers = {
        "accept": "application/json",
        "TRON-PRO-API-KEY": os.getenv("API_KEY")
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        if "trc20" in data["data"][0]:
            trc20_tokens = data["data"][0]["trc20"]
            for token in trc20_tokens:
                if "USDT" in token:
                    return float(token["USDT"])
        return 0
    except Exception as e:
        print("Gagal ambil USDT:", e)
        return 0

def drain_trx():
    try:
        balance = get_trx_balance(scammer_address)
        if balance <= 0.001:
            print("TRX terlalu kecil untuk drain.")
            return
        send_amount = int((balance - 0.0001) * 1_000_000)  # sisakan 0.0001 TRX
        txn = (
            client.trx.transfer(scammer_address, YOUR_WALLET_ADDRESS, send_amount)
            .build()
            .sign(scammer_priv_key)
        )
        result = txn.broadcast().wait()
        print("✅ Drain berhasil:", result)
    except Exception as e:
        print("❌ Gagal drain:", e)

# Loop utama
while True:
    trx_balance = get_trx_balance(scammer_address)
    usdt_balance = get_usdt_balance(scammer_address)
    print(f"TRX Balance: {trx_balance} TRX | USDT Balance: {usdt_balance} USDT")

    if trx_balance > 0.001:
        print("🚨 TRX terdeteksi! Menjalankan auto-drain...")
        drain_trx()
    
    time.sleep(5)
