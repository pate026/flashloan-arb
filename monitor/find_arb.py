#!/usr/bin/env python3
"""
find_arb.py - Etsii optimaalisen flash loan -arbitraasin koon (Arbitrum, ARB/WETH).
"""

import os
import sys
from web3 import Web3

QUOTER_V2 = Web3.to_checksum_address("0x61fFE014bA17989E743c5F6cB21bF9697530B21e")

# Tokenit (Arbitrum native) - HUOM: ARB:lla 18 desimaalia, ei 6!
ARB = Web3.to_checksum_address("0x912CE59144191C1204E64559FE8253a0e49E6548")   # 18 desim.
WETH = Web3.to_checksum_address("0x82aF49447D8a07e3bd95BD0d56f35241523fBab1")  # 18 desim.

AAVE_PREMIUM_BPS = 5

FEE_BUY = 3000    # leg 1: ARB -> WETH (0.3%)
FEE_SELL = 10000  # leg 2: WETH -> ARB (1%)

# Panoskoot ARB:n yksikoissa (18 desimaalia)
TEST_AMOUNTS_ARB = [1_000, 5_000, 10_000, 25_000, 50_000, 100_000]

QUOTER_ABI = [
    {
        "inputs": [
            {
                "components": [
                    {"internalType": "address", "name": "tokenIn", "type": "address"},
                    {"internalType": "address", "name": "tokenOut", "type": "address"},
                    {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
                    {"internalType": "uint24", "name": "fee", "type": "uint24"},
                    {"internalType": "uint160", "name": "sqrtPriceLimitX96", "type": "uint160"},
                ],
                "internalType": "struct IQuoterV2.QuoteExactInputSingleParams",
                "name": "params",
                "type": "tuple",
            }
        ],
        "name": "quoteExactInputSingle",
        "outputs": [
            {"internalType": "uint256", "name": "amountOut", "type": "uint256"},
            {"internalType": "uint160", "name": "sqrtPriceX96After", "type": "uint160"},
            {"internalType": "uint32", "name": "initializedTicksCrossed", "type": "uint32"},
            {"internalType": "uint256", "name": "gasEstimate", "type": "uint256"},
        ],
        "stateMutability": "nonpayable",
        "type": "function",
    }
]


def get_quote(quoter, token_in, token_out, amount_in, fee):
    params = (token_in, token_out, amount_in, fee, 0)
    return quoter.functions.quoteExactInputSingle(params).call()[0]


def main():
    rpc_url = os.environ.get("ARBITRUM_RPC_URL")
    if not rpc_url:
        print("VIRHE: ARBITRUM_RPC_URL puuttuu.")
        sys.exit(1)

    w3 = Web3(Web3.HTTPProvider(rpc_url))
    if not w3.is_connected():
        print("VIRHE: Ei yhteytta RPC:hen.")
        sys.exit(1)

    print(f"Yhdistetty Arbitrumiin. Lohko: {w3.eth.block_number}")
    print(f"Reitti: ARB --({FEE_BUY/10000:.2f}%)--> WETH --({FEE_SELL/10000:.2f}%)--> ARB")
    print(f"Aave-preemio: {AAVE_PREMIUM_BPS/100:.2f}%")
    print("-" * 72)

    quoter = w3.eth.contract(address=QUOTER_V2, abi=QUOTER_ABI)

    best_profit = -(2**256)
    best_amount = 0

    for amount_arb in TEST_AMOUNTS_ARB:
        amount_in = amount_arb * 10**18  # ARB 18 desimaalia

        try:
            weth_out = get_quote(quoter, ARB, WETH, amount_in, FEE_BUY)
            arb_back = get_quote(quoter, WETH, ARB, weth_out, FEE_SELL)
        except Exception as e:
            print(f"{amount_arb:>10,} ARB | quote epaonnistui: {e}")
            continue

        amount_owed = amount_in + (amount_in * AAVE_PREMIUM_BPS) // 10_000
        profit_raw = arb_back - amount_owed
        profit_arb = profit_raw / 10**18

        marker = ""
        if profit_raw > best_profit:
            best_profit = profit_raw
            best_amount = amount_arb
            marker = "  <-- paras toistaiseksi"

        status = "VOITTO" if profit_arb > 0 else "tappio"
        print(f"{amount_arb:>10,} ARB | {status}: {profit_arb:>12,.2f} ARB{marker}")

    print("-" * 72)

    if best_profit > 0:
        print(f"PARAS: {best_amount:,} ARB lainalla -> "
              f"~{best_profit/10**18:,.2f} ARB voitto (ennen gas-kuluja)")
    else:
        print("Ei kannattavaa arbitraasia nailla fee-tiereilla juuri nyt.")


if __name__ == "__main__":
    main()
