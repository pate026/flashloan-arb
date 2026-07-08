import json
from pathlib import Path


ABI_DIR = Path(__file__).parent / "abi"


def load_abi(filename: str):

    path = ABI_DIR / filename

    if not path.exists():
        raise FileNotFoundError(
            f"ABI-tiedostoa ei löytynyt: {path}"
        )

    with open(path, "r", encoding="utf-8") as f:
        abi = json.load(f)

    if not isinstance(abi, list):
        raise TypeError(
            f"{filename} ei sisällä kelvollista ABI-listaa."
        )

    if len(abi) == 0:
        raise ValueError(
            f"{filename} on tyhjä."
        )

    return abi
