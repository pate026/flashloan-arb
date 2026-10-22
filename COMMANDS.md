# Komentolista - flashloan-arb

Pikaviite yleisimpiin komentoihin. Muista: Termux ei sailyta
ymparistomuuttujia istuntojen valilla - export-komennot pitaa ajaa uudelleen
joka kerta kun avaat uuden Termux-session.

## Joka session alussa

```bash
cd ~/flashloan-arb
export ARBITRUM_RPC_URL="https://arb-mainnet.g.alchemy.com/v2/OIKEA_AVAIN"
export ETHERSCAN_API_KEY="OIKEA_AVAIN"
echo $ARBITRUM_RPC_URL   # varmista ettei ole tyhja
```

## Navigointi

```bash
pwd                          # missa olen nyt
ls                           # mita tassa kansiossa on
cd ~/flashloan-arb           # projektin juureen
cd ~/flashloan-arb/monitor   # python-skriptien kansioon
```

## Tiedoston muokkaus (nano)

```bash
> tiedosto.py                # TYHJENTAA tiedoston valittomasti (huom: > ei >>)
nano tiedosto.py              # avaa muokattavaksi - liita koodi TASSA sisalla
```

Nanossa: Ctrl+O tallenna, Enter vahvista, Ctrl+X sulje.
Ala koskaan liita koodia suoraan $-kehotteeseen - vain nanon sisalle.

## Foundry - kaannos ja testaus

```bash
forge build                              # kaanna kaikki kontraktit
forge test --fork-url $ARBITRUM_RPC_URL -vvv   # aja kaikki testit fork-tilassa
forge clean                              # siivoa vanhat build-artifaktit
```

## Foundry - deploy

```bash
forge script script/DeployFlashLoanArb.s.sol \
  --rpc-url $ARBITRUM_RPC_URL \
  --chain 42161 \
  --account pate026 \
  --broadcast
```

## Foundry - verify (Arbiscan/Polygonscan)

```bash
forge verify-contract \
  <OSOITE> \
  src/FlashLoanArb.sol:FlashLoanArb \
  --chain 42161 \
  --constructor-args $(cast abi-encode "constructor(address)" 0xa97684ead0e402dC232d5A977953DF7ECBaB3CDb) \
  --etherscan-api-key $ETHERSCAN_API_KEY \
  --watch
```

## Cast - lompakko ja transaktiot

```bash
cast wallet import pate026 --interactive     # tuo private key kertaalleen, salattuna

cast send <KONTRAKTI_OSOITE> \
  "setRouterAllowed(address,bool)" \
  <ROUTER_OSOITE> \
  true \
  --rpc-url $ARBITRUM_RPC_URL \
  --account pate026
```

## Git-workflow

```bash
git status                   # mita on muuttunut
git add .                    # lisaa kaikki muutokset
git add -A                   # sama, mutta huomioi myos poistot
git commit -m "Viesti"       # committaa
git push                     # laheta GitHubiin
diff tiedosto1 tiedosto2      # vertaa kahta tiedostoa
```

## Python-skriptit (monitor/-kansiossa)

```bash
cd ~/flashloan-arb/monitor

python3 find_arb.py                # kertaskannaus - onko arbitraasia juuri nyt
python3 monitor_arb.py             # jatkuva seuranta 10s valein (Ctrl+C lopettaa)
python3 find_arb_cross_dex.py      # Uniswap vs Camelot -vertailu
```

## Tunnetut osoitteet (Arbitrum One, chain 42161)

| Mika | Osoite |
|---|---|
| Aave PoolAddressesProvider | `0xa97684ead0e402dC232d5A977953DF7ECBaB3CDb` |
| Uniswap V3 SwapRouter | `0xE592427A0AEce92De3Edee1F18E0157C05861564` |
| Uniswap V3 QuoterV2 | `0x61fFE014bA17989E743c5F6cB21bF9697530B21e` |
| Camelot V3 Quoter | `0x0Fc73040b26E9bC8514fA028D998E73A254Fa76E` |
| USDC (native) | `0xaf88d065e77c8cC2239327C5EDb3A432268e5831` |
| WETH | `0x82aF49447D8a07e3bd95BD0d56f35241523fBab1` |

## Deployatut kontraktit

| Verkko | Osoite |
|---|---|
| Polygon (137) | `0x332b65f75DDBf4F351eabbD86aAf34b7025321F2` |
| Arbitrum (42161) | `0x140cc8CC299A43862b12939a5008094CD14009dD` |

## Yleisimmat virheet ja korjaukset

| Virhe | Syy | Korjaus |
|---|---|---|
| `Failed to fetch` (Remix) | Vaara import-polku | Kayta `@aave/core-v3/...` -muotoa |
| `bytecode_length_mismatch` | ETHERSCAN_API_KEY kadonnut istunnosta | `export` uudelleen |
| `command not found` (bash) | Koodi liitetty suoraan komentoriville | Kayta aina `nano tiedosto.py` ensin |
| `call to non-contract address` | Vaaran ketjun token-osoite testissa | Tarkista etta osoite on oikean verkon |
