from web3 import Web3

from dex import w3
from uniswap import get_uniswap_pool
from config import TOKENS

POOL_ABI = [
    {
        "inputs": [],
        "name": "slot0",
        "outputs": [
            {"internalType": "uint160", "name": "sqrtPriceX96", "type": "uint160"},
            {"internalType": "int24", "name": "tick", "type": "int24"},
            {"internalType": "uint16", "name": "observationIndex", "type": "uint16"},
            {"internalType": "uint16", "name": "observationCardinality", "type": "uint16"},
            {"internalType": "uint16", "name": "observationCardinalityNext", "type": "uint16"},
            {"internalType": "uint8", "name": "feeProtocol", "type": "uint8"},
            {"internalType": "bool", "name": "unlocked", "type": "bool"}
        ],
        "stateMutability": "view",
        "type": "function"
    }
]


def read_slot0(pool_address):

    pool = w3.eth.contract(
        address=Web3.to_checksum_address(pool_address),
        abi=POOL_ABI,
    )

    return pool.functions.slot0().call()


def get_uniswap_price():

    pool = get_uniswap_pool(
        TOKENS["WMATIC"],
        TOKENS["USDC"],
        500,
    )

    slot0 = read_slot0(pool)

    return {
        "pool": pool,
        "sqrtPriceX96": slot0[0],
        "tick": slot0[1],
        "block": w3.eth.block_number,
    }


if __name__ == "__main__":

    data = get_uniswap_price()

    print("\n=== Uniswap V3 ===")
    print(f"Pool : {data['pool']}")
    print(f"Block: {data['block']}")
    print(f"Tick : {data['tick']}")
    print(f"sqrt : {data['sqrtPriceX96']}")
