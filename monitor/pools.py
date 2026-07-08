from uniswap import get_uniswap_pool
from quickswap import get_quickswap_pool
from config import TOKENS

PAIR = (
    TOKENS["WMATIC"],
    TOKENS["USDC"],
)

if __name__ == "__main__":

    print("Haetaan poolit...\n")

    uni = get_uniswap_pool(*PAIR, 500)
    print(f"Uniswap V3 : {uni}")

    quick = get_quickswap_pool(*PAIR)
    print(f"QuickSwap V3: {quick}")
