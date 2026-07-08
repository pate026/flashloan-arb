from web3 import Web3

from config import RPC_URL

if RPC_URL is None:
    raise RuntimeError(
        "POLYGON_RPC_URL ei ole asetettu. "
        "Suorita: export POLYGON_RPC_URL=https://..."
    )

w3 = Web3(Web3.HTTPProvider(RPC_URL))

if not w3.is_connected():
    raise RuntimeError("Yhteys Polygon RPC:hen epäonnistui.")

print(f"Yhdistetty Polygoniin.")
print(f"Lohko: {w3.eth.block_number}")
