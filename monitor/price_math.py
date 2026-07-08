from decimal import Decimal, getcontext

getcontext().prec = 80

Q96 = Decimal(2**96)


def sqrt_price_x96_to_price(
    sqrt_price_x96: int,
    decimals_token0: int,
    decimals_token1: int,
    inverse: bool = False,
) -> Decimal:
    """
    Muuntaa Uniswap V3:n sqrtPriceX96-arvon hinnaksi.

    inverse=False:
        token1 per token0

    inverse=True:
        token0 per token1
    """

    sqrt_price = Decimal(sqrt_price_x96)

    price = (sqrt_price * sqrt_price) / (Q96 * Q96)

    decimal_adjustment = Decimal(
        10 ** (decimals_token0 - decimals_token1)
    )

    price *= decimal_adjustment

    if inverse:
        return Decimal(1) / price

    return price


def price_to_float(
    sqrt_price_x96: int,
    decimals_token0: int,
    decimals_token1: int,
    inverse: bool = False,
) -> float:

    return float(
        sqrt_price_x96_to_price(
            sqrt_price_x96,
            decimals_token0,
            decimals_token1,
            inverse,
        )
    )


if __name__ == "__main__":

    sqrt_price = 21984164955113384702474

    print("token1/token0:")
    print(
        price_to_float(
            sqrt_price,
            18,
            6,
            False,
        )
    )

    print()

    print("token0/token1:")
    print(
        price_to_float(
            sqrt_price,
            18,
            6,
            True,
        )
    )
