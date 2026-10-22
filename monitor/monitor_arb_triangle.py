#!/usr/bin/env python3
"""
monitor_arb_triangle.py - Kolmiomainen flash loan -arbitraasi (Arbitrum).
Reitti: USDC -> WETH -> ARB -> USDC. Leg-by-leg -erittely.
Vain-luku: ei private keyta, ei transaktioita.
"""

import os
import sys
import time
from datetime import datetime
from web3 import Web3

CHECK_INTERVAL_SEC = 10
MIN_PROFIT_USDC = 1.0

# Yksi panoskoko kerrallaan, jotta erittely on selkea
TEST_AMOUNT_USDC = 100

QUOTER_V2 = Web3.to_checksum_address("0x61fFE014bA17989E743c5F6cB21bF9697530B21e")
USDC = Web3.to_checksum_address("0xaf88d065e77c8cC2239327C5EDb3A432268e5831")  # 6 desim.
WETH = Web3.to_checksum_address("0x82aF49447D8a07e3bd95BD0d56f35241523fBab1")  # 18 desim.
ARB  = Web3.to_checksum_address("0x912CE59144191C1204E64559FE8253a0e49E6548")  # 18 desim.

AAVE_PREMIUM_BPS = 5

FEE_LEG1 = 500    # USDC -> WETH
FEE_LEG2 = 500    # WETH -> ARB
FEE_LEG3 = 500    # ARB  -> USDC

# Karkeat USD-hinnat vain erittelyn dollariarvoja varten (paivita tarvittaessa)
# Naita EI kayteta voittolaskennassa - se on aina tarkka on-chain quote.
PRICE_WETH_USD = 1680.0
PRICE_ARB_USD = 0.125

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
    amount_in = TEST_AMOUNT_USDC * 10**6          # USDC 6 desim.
    try:
        weth_out = get_quote(quoter, USDC, WETH, amount_in, FEE_LEG1)
        arb_out  = get_quote(quoter, WETH, ARB,  weth_out, FEE_LEG2)
        usdc_back = get_quote(quoter, ARB, USDC, arb_out, FEE_LEG3)
    except Exception as e:
        return None

    # Muunna dollariarvoiksi erittelya varten
    usd_start = TEST_AMOUNT_USDC
    usd_after_leg1 = (weth_out / 10**18) * PRICE_WETH_USD
    usd_after_leg2 = (arb_out / 10**18) * PRICE_ARB_USD
    usd_after_leg3 = usdc_back / 10**6

    amount_owed = amount_in + (amount_in * AAVE_PREMIUM_BPS) // 10_000
    profit_usdc = (usdc_back - amount_owed) / 10**6

    return {
        "profit": profit_usdc,
        "usd_start": usd_start,
        "leg1": usd_after_leg1,
        "leg2": usd_after_leg2,
        "leg3": usd_after_leg3,
    }


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

    print("Kolmioarbitraasi + leg-erittely: USDC -> WETH -> ARB -> USDC")
    print(f"Panos: {TEST_AMOUNT_USDC} USDC | Fee: {FEE_LEG1/10000}%/{FEE_LEG2/10000}%/{FEE_LEG3/10000}%")
    print("Dollariarvot ovat likimaaraisia (vain erittelya varten).")
    print("Lopeta: Ctrl+C")
    print("-" * 72)

    checks = 0
    best_seen = None
    start = time.time()

    try:
        while True:
            checks += 1
            r = check_once(quoter)
            ts = datetime.now().strftime("%H:%M:%S")
            if r is None:
                print(f"[{ts}] quote epaonnistui (tarkista fee-tierit / poolit)")
            else:
                if best_seen is None or r["profit"] > best_seen:
                    best_seen = r["profit"]
                print(f"[{ts}] voitto: {r['profit']:+.4f} USDC")
                print(f"         start ${r['usd_start']:.2f}"
                      f" -> leg1(WETH) ${r['leg1']:.2f}"
                      f" -> leg2(ARB) ${r['leg2']:.2f}"
                      f" -> leg3(USDC) ${r['leg3']:.2f}")
                # Nayta paljonko kussakin legissa hävisi/voitti dollareina
                d1 = r["leg1"] - r["usd_start"]
                d2 = r["leg2"] - r["leg1"]
                d3 = r["leg3"] - r["leg2"]
                print(f"         muutos:   leg1 {d1:+.2f}   leg2 {d2:+.2f}   leg3 {d3:+.2f}")
            time.sleep(CHECK_INTERVAL_SEC)
    except KeyboardInterrupt:
        elapsed = time.time() - start
        print("\n" + "-" * 72)
        print("SEURANTA LOPETETTU.")
        print(f"  Kesto: {elapsed/60:.1f} min | Tarkistuksia: {checks}")
        if best_seen is not None:
            print(f"  Paras nahty: {best_seen:+.4f} USDC")
        print("-" * 72)


if __name__ == "__main__":
    main()
