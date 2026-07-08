from web3 import Web3

from abi_loader import load_abi
from config import DEX
from dex import w3

FACTORY_ABI = load_abi("algebra_factory.json")

factory = w3.eth.contract(
    address=Web3.to_checksum_address(
        DEX["QUICKSWAP_V3_FACTORY"]
    ),
    abi=FACTORY_ABI,
)


def get_quickswap_pool(token0, token1):

    return factory.functions.poolByPair(
        Web3.to_checksum_address(token0),
        Web3.to_checksum_address(token1),
    ).call()


if __name__ == "__main__":

    from config import TOKENS

    pool = get_quickswap_pool(
        TOKENS["WMATIC"],
        TOKENS["USDC"],
    )

    print(pool)
