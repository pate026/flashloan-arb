#!/usr/bin/env python3
"""
monitor_arb_pepe.py - Jatkuva flash loan -arbitraasin seuranta PEPE/WETH-parilla (Arbitrum).
HUOM: PEPE-likviditeetti on todella ohutta - kaytetaan pienia panoskokoja.
"""

import os
import sys
import time
from datetime import datetime
from web3 import Web3

CHECK_INTERVAL_SEC = 10
MIN_PROFIT_PEPE = 1_000_000  # 1M PEPE (koska hinta on niin pieni)

TEST_AMOUNTS_PEPE = [1_000_000, 5_000_000, 10_000_000, 25_000_000]

QUOTER_V2 = Web3.to_checksum_address("0x61fFE014bA17989E743c5F6cB21bF9697530B21e")
PEPE = Web3.to_checksum_address("0x25d887Ce7a35172C62FeBFD67a1856F20FaEBB00")  # 18 desim.
WETH = Web3.to_checksum_address("0x82aF49447D8a07e3bd95BD0d56f35241523fBab1")

AAVE_PREMIUM_BPS = 5
FEE_BUY = 3000    # 0.3% pooli
FEE_SELL = 10000  # 1% pooli

QUOTER_ABI = [
    {
        "inputs": [{
            "components": [
                {"internalType": "address", "name": "tokenIn", "type": "address"},
                {"internalType": "address", "name": "tokenOut", "type": "address"},
                {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
                {"internalType": "uint24", "name": "fee", "type": "uint24"},
                {"internalType": "uint160", "name": "sqrtPriceLimitX96", "type": "uint160"},
            ],
            "internalType": "struct IQuoterV2.QuoteExactInputSingleParams",
            "name": "params", "type": "tuple",
        }],
        "name": "quoteExactInputSingle",
        "outputs": [
            {"internalType": "uint256", "name": "amountOut", "type": "uint256"},
            {"internalType": "uint160", "name": "sqrtPriceX96After", "type": "uint160"},
            {"internalType": "uint32", "name": "initializedTicksCrossed", "type": "uint32"},
            {"internalType": "uint256", "name": "gasEstimate", "type": "uint256"},
        ],
        "stateMutability": "nonpayable", "type": "function",
    }
]


def get_quote(quoter, token_in, token_out, amount_in, fee):
    params = (token_in, token_out, amount_in, fee, 0)
    return quoter.functions.quoteExactInputSingle(params).call()[0]


def check_once(quoter):
    best_profit = None
    best_amount = 0
    for amount_pepe in TEST_AMOUNTS_PEPE:
        amount_in = amount_pepe * 10**18
        try:
            weth_out = get_quote(quoter, PEPE, WETH, amount_in, FEE_BUY)
            pepe_back = get_quote(quoter, WETH, PEPE, weth_out, FEE_SELL)
        except Exception:
            continue
        amount_owed = amount_in + (amount_in * AAVE_PREMIUM_BPS) // 10_000
        profit_pepe = (pepe_back - amount_owed) / 10**18
        if best_profit is None or profit_pepe > best_profit:
            best_profit = profit_pepe
            best_amount = amount_pepe
    return best_profit, best_amount


def alert(profit, amount):
    print("\a")
    print("=" * 72)
    print(f"  !!! MAHDOLLISUUS LOYTYI !!!")
    print(f"  Panos: {amount:,} PEPE  ->  voitto: ~{profit:,.0f} PEPE")
    print(f"  Aika: {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 72)


def main():
    rpc_url = os.environ.get("ARBITRUM_RPC_URL")
    if not rpc_url:
        print("VIRHE: ARBITRUM_RPC_URL puuttuu.")
        sys.exit(1)

    w3 = Web3(Web3.HTTPProvider(rpc_url))
    if not w3.is_connected():
        print("VIRHE: Ei yhteytta RPC:hen.")
        sys.exit(1)

    quoter = w3.eth.contract(address=QUOTER_V2, abi=QUOTER_ABI)

    print("PEPE/WETH seuranta kaynnistetty (0.3% vs 1% pooli).")
    print(f"Tarkistusvali: {CHECK_INTERVAL_SEC}s")
    print("Lopeta: Ctrl+C")
    print("-" * 72)

    checks = 0
    opportunities = 0
    best_seen = None
    start = time.time()

    try:
        while True:
            checks += 1
            best_profit, best_amount = check_once(quoter)
            if best_profit is None:
                print("quote epaonnistui")
            else:
                if best_seen is None or best_profit > best_seen:
                    best_seen = best_profit
                ts = datetime.now().strftime("%H:%M:%S")
                block = w3.eth.block_number
                print(f"[{ts}] lohko {block} | paras: {best_profit:>14,.0f} PEPE ({best_amount:,} panos)")
                if best_profit >= MIN_PROFIT_PEPE:
                    opportunities += 1
                    alert(best_profit, best_amount)
            time.sleep(CHECK_INTERVAL_SEC)
    except KeyboardInterrupt:
        elapsed = time.time() - start
        print("\n" + "-" * 72)
        print("SEURANTA LOPETETTU.")
        print(f"  Kesto: {elapsed/60:.1f} min | Tarkistuksia: {checks} | Mahdollisuuksia: {opportunities}")
        if best_seen is not None:
            print(f"  Paras nahty: {best_seen:,.0f} PEPE")
        print("-" * 72)


if __name__ == "__main__":
    main()
