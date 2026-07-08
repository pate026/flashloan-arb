from web3 import Web3

from dex import w3
from uniswap import get_uniswap_pool
from config import TOKENS

ABI = [
    {
        "inputs": [],
        "name": "token0",
        "outputs": [{"type": "address"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "token1",
        "outputs": [{"type": "address"}],
        "stateMutability": "view",
        "type": "function",
    },
]

pool = get_uniswap_pool(
    TOKENS["WMATIC"],
    TOKENS["USDC"],
    500,
)

contract = w3.eth.contract(
    address=Web3.to_checksum_address(pool),
    abi=ABI,
)

print("Pool :", pool)
print("token0:", contract.functions.token0().call())
print("token1:", contract.functions.token1().call())
