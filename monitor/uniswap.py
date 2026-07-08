import json
from pathlib import Path

from web3 import Web3

from dex import w3
from config import DEX


ABI_PATH = Path(__file__).parent / "abi" / "uniswap_factory.json"

with open(ABI_PATH, "r") as f:
    FACTORY_ABI = json.load(f)


factory = w3.eth.contract(
    address=Web3.to_checksum_address(
        DEX["UNISWAP_V3_FACTORY"]
    ),
    abi=FACTORY_ABI,
)


def get_uniswap_pool(token0, token1, fee):

    return factory.functions.getPool(
        Web3.to_checksum_address(token0),
        Web3.to_checksum_address(token1),
        fee,
    ).call()


if __name__ == "__main__":

    from config import TOKENS

    pool = get_uniswap_pool(
        TOKENS["WMATIC"],
        TOKENS["USDC"],
        500,
    )

    print(pool)
