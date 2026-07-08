# flashloan-arb

Aave V3 flash loan -pohjainen arbitraasisopimus Solidityssa, testattu ja deployattu
Polygon- ja Arbitrum-mainnetille. Projekti sisältää myös off-chain Python-työkalut
arbitraasimahdollisuuksien etsintään.

## Mikä tämä on

`FlashLoanArb.sol` lainaa varoja Aave V3:n `flashLoanSimple`-toiminnolla, tekee
kaksi peräkkäistä swappia (asset → tokenMid → asset) kahden DEX-routerin/fee-tierin
välillä, ja tarkistaa lopuksi että voitto ylittää `minProfit`-rajan. Jos ei ylitä,
koko transaktio reverttaa atomisesti — pahin mahdollinen tappio on aina vain gas,
ei koskaan lainapääoma.

## Arkkitehtuuri

- `FlashLoanSimpleReceiverBase` (Aave V3) + `Ownable` (OpenZeppelin v5)
- `allowedRouters`-whitelist: vain omistajan hyväksymät routerit kelpaavat swappeihin
- `SafeERC20`/`forceApprove` kaikissa token-siirroissa
- Koko kannattavuustarkistus yhdessä paikassa transaktion lopussa (suojaa myös slippagelta)

## Deploymentit

| Verkko | Osoite | Status |
|---|---|---|
| Polygon mainnet (137) | `0x332b65f75DDBf4F351eabbD86aAf34b7025321F2` | Verifioitu, `allowedRouters` asetettu |
| Arbitrum One (42161) | `0x140cc8CC299A43862b12939a5008094CD14009dD` | Verifioitu, `allowedRouters` asetettu |

Aave PoolAddressesProvider (Polygon/Arbitrum/Optimism, sama osoite): `0xa97684ead0e402dC232d5A977953DF7ECBaB3CDb`

## Testaus

Foundry fork-testit (`test/`) kattavat:
- Realistinen fork-testi oikealla mainnet-datalla (odottaa "ei kannattava" -revertiä)
- `MockRouter`-testi pakotetulla kannattavalla skenaariolla — todistaa että itse
  kontraktilogiikka (approve, voittotarkistus, event) toimii oikein
- Owner-only-tarkistus

Aja: `forge test --fork-url $RPC_URL -vvv`

## Arbitraasin etsintä — tulokset

Off-chain Python-skriptit (`monitor/`) kyselevät Uniswap V3:n ja Camelot V3:n
(Algebra) Quoter-kontrakteilta hintoja `web3.py`:llä. Testattiin viisi eri
yhdistelmää:

| Ketju | Pari | Menetelmä | Tulos |
|---|---|---|---|
| Polygon | USDC/WETH | sama DEX, eri fee-tierit | tappiollinen |
| Arbitrum | USDC/WETH | sama DEX, eri fee-tierit | tappiollinen |
| Arbitrum | ARB/WETH | sama DEX, eri fee-tierit | tappiollinen |
| Arbitrum | USDC/WETH | cross-DEX (Uniswap↔Camelot) | tappiollinen |
| Arbitrum | GMX/WETH | cross-DEX (Uniswap↔Camelot) | tappiollinen |

**Johtopäätös:** yhdelläkään testatulla ketju/pari/menetelmä-yhdistelmällä ei
löytynyt kannattavaa mahdollisuutta millään panoskoolla. Tappio kasvaa
epälineaarisesti panoskoon mukana (hintavaikutus), ja MEV-botit pitävät
suositut parit hyvin linjassa jopa ohuemman likviditeetin poolissa (GMX).

## Mitä opittiin

- Saman DEX:n eri fee-tierien välinen arbitraasi ei ole hedelmällinen alue
  suosituilla pareilla — botit tasapainottavat hinnat sekunneissa.
- Cross-DEX (eri protokollien välillä) on periaatteessa lupaavampi, mutta ei
  auttanut käytä
