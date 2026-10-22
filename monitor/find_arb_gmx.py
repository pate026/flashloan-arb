#!/usr/bin/env python3
"""
find_arb_gmx.py - Etsii arbitraasin GMX/WETH-parilla Uniswap V3:n ja Camelot V3:n valilla Arbitrumilla.

TURVALLINEN: Vain laskee ja tulostaa, ei laheta transaktioita.
HUOM: GMX on paljon ohuempi likviditeetti kuin USDC/WETH, joten kaytetaan
paljon pienempia panoskokoja - isot summat aiheuttaisivat massiivisen slippagen.
"""

import os
import sys
from web3 import Web3

UNI_QUOTER = Web3.to_checksum_address("0x61fFE014bA17989E743c5F6cB21bF9697530B21e")
CAMELOT_QUOTER = Web3.to_checksum_address("0x0Fc73040b26E9bC8514fA028D998E73A254Fa76E")

GMX = Web3.to_checksum_address("0xfc5A1A6EB076a2C7aD06eD22C90d7E710E35ad0a")   # 18 desim.
WETH = Web3.to_checksum_address("0x82aF49447D8a07e3bd95BD0d56f35241523fBab1")  # 18 desim.

AAVE_PREMIUM_BPS = 5
UNI_FEE = 10000  # GMX/WETH-poolin fee-tieri Uniswapilla on 1%

# Paljon pienempia summia kuin USDC-testeissa - GMX-likviditeetti on ohutta
TEST_AMOUNTS_GMX = [10, 50, 100, 250, 500]

UNI_QUOTER_ABI = [
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

CAMELOT_QUOTER_ABI = [
    {
        "inputs": [
            {"internalType": "address", "name": "tokenIn", "type": "address"},
            {"internalType": "address", "name": "tokenOut", "type": "address"},
            {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
            {"internalType": "uint160", "name": "limitSqrtPrice", "type": "uint160"},
        ],
        "name": "quoteExactInputSingle",
        "outputs": [
            {"internalType": "uint256", "name": "amountOut", "type": "uint256"},
            {"internalType": "uint16", "name": "fee", "type": "uint16"},
        ],
        "stateMutability": "nonpayable",
        "type": "function",
    }
]


def uni_quote(quoter, token_in, token_out, amount_in, fee=UNI_FEE):
    params = (token_in, token_out, amount_in, fee, 0)
    result = quoter.functions.quoteExactInputSingle(params).call()
    return result[0]


def camelot_quote(quoter, token_in, token_out, amount_in):
    result = quoter.functions.quoteExactInputSingle(token_in, token_out, amount_in, 0).call()
    return result[0]


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
    print("Vertaillaan Uniswap V3 <-> Camelot V3 (Algebra), GMX/WETH")
    print("HUOM: GMX-likviditeetti on ohutta - odota isoa hintavaikutusta")
    print("-" * 78)

    uni = w3.eth.contract(address=UNI_QUOTER, abi=UNI_QUOTER_ABI)
    cam = w3.eth.contract(address=CAMELOT_QUOTER, abi=CAMELOT_QUOTER_ABI)

    best_profit = -(2**256)
    best_desc = ""

    for amount_gmx in TEST_AMOUNTS_GMX:
        amount_in = amount_gmx * 10**18
        amount_owed = amount_in + (amount_in * AAVE_PREMIUM_BPS) // 10_000

        try:
            weth_out_a = uni_quote(uni, GMX, WETH, amount_in)
            gmx_back_a = camelot_quote(cam, WETH, GMX, weth_out_a)
            profit_a = (gmx_back_a - amount_owed) / 10**18
        except Exception as e:
            profit_a = None
            print(f"{amount_gmx:>6,} GMX | Uni->Camelot quote epaonnistui: {e}")

        try:
            weth_out_b = camelot_quote(cam, GMX, WETH, amount_in)
            gmx_back_b = uni_quote(uni, WETH, GMX, weth_out_b)
            profit_b = (gmx_back_b - amount_owed) / 10**18
        except Exception as e:
            profit_b = None
            print(f"{amount_gmx:>6,} GMX | Camelot->Uni quote epaonnistui: {e}")

        if profit_a is not None:
            status = "VOITTO" if profit_a > 0 else "tappio"
            print(f"{amount_gmx:>6,} GMX | Uni->Camelot | {status}: {profit_a:>10,.4f} GMX")
            if profit_a > best_profit:
                best_profit = profit_a
                best_desc = f"{amount_gmx:,} GMX, Uni->Camelot"

        if profit_b is not None:
            status = "VOITTO" if profit_b > 0 else "tappio"
            print(f"{amount_gmx:>6,} GMX | Camelot->Uni | {status}: {profit_b:>10,.4f} GMX")
            if profit_b > best_profit:
                best_profit = profit_b
                best_desc = f"{amount_gmx:,} GMX, Camelot->Uni"

    print("-" * 78)
    if best_profit > 0:
        print(f"PARAS: {best_desc} -> ~{best_profit:,.4f} GMX voitto (ennen gas-kuluja)")
    else:
        print(f"Ei kannattavaa arbitraasia juuri nyt. Paras nahty: {best_profit:,.4f} GMX")


if __name__ == "__main__":
    main()
