from web3 import Web3

from abi_loader import load_abi
from config import DEX
from dex import w3

QUOTER_ABI = load_abi("uniswap_quoter.json")

quoter = w3.eth.contract(
    address=Web3.to_checksum_address(
        DEX["UNISWAP_V3_QUOTER"]
    ),
    abi=QUOTER_ABI,
)


def quote_exact_input_single(
    token_in,
    token_out,
    fee,
    amount_in,
):
    params = (
        Web3.to_checksum_address(token_in),
        Web3.to_checksum_address(token_out),
        fee,
        amount_in,
        0,
    )

    return quoter.functions.quoteExactInputSingle(
        params
    ).call()


if __name__ == "__main__":

    from config import TOKENS

    result = quote_exact_input_single(
        TOKENS["USDC"],
        TOKENS["WMATIC"],
        500,
        1_000_000,
    )

    print(result)
