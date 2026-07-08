# FlashLoanArb

A Solidity-based flash loan arbitrage project built with **Foundry** using **Aave V3 Flash Loans** and **Uniswap V3**. The project also includes a Python monitor that searches for potential arbitrage opportunities without sending transactions.

> **Status:** Learning project / Work in progress

---

# Overview

The goal of this project is to learn how flash loans and decentralized exchange (DEX) arbitrage work in practice.

The project consists of two main parts:

- **Smart Contract**
  - Requests a flash loan from Aave V3.
  - Executes a two-leg swap.
  - Repays the loan and Aave premium.
  - Keeps any remaining profit.

- **Python Monitor**
  - Connects to Polygon through an RPC provider.
  - Reads prices from supported DEXes.
  - Estimates whether an arbitrage opportunity exists.
  - Never sends transactions.

---

# How Flash Loans Work

A flash loan allows you to borrow assets without collateral.

The only requirement is:

- borrow funds
- perform all operations
- repay the loan plus the Aave premium
- complete everything inside **one blockchain transaction**

If repayment fails, the entire transaction is reverted.

No loan is issued and all state changes are cancelled.

---

# Arbitrage Flow

```
Borrow USDC from Aave

↓

Swap USDC → WETH

↓

Swap WETH → USDC

↓

Repay loan + Aave premium

↓

Keep remaining profit
```

If the trade is not profitable, the transaction reverts automatically.

---

# Project Structure

```
flashloan-arb/

├── src/
│   └── FlashLoanArb.sol
│
├── script/
│   └── DeployFlashLoanArb.s.sol
│
├── test/
│   ├── FlashLoanArb.t.sol
│   └── FlashLoanArbForcedProfit.t.sol
│
├── monitor/
│   ├── monitor_arb.py
│   ├── find_arb.py
│   ├── config.py
│   ├── abi_loader.py
│   └── ...
│
└── README.md
```

---

# Features

- Aave V3 Flash Loans
- Uniswap V3 integration
- Router whitelist
- Owner-only execution
- SafeERC20 support
- Reentrancy protection
- Fork testing
- Read-only arbitrage monitor

---

# Prerequisites

Install:

- Foundry
- Python 3
- Web3.py

Example:

```bash
pip install web3
```

You also need a Polygon RPC endpoint.

Example:

```
POLYGON_RPC
---

# Deployments

| Network | Address | Status |
|---|---|---|
| Polygon mainnet (137) | `0x332b65f75DDBf4F351eabbD86aAf34b7025321F2` | Verified, `allowedRouters` set |
| Arbitrum One (42161) | `0x140cc8CC299A43862b12939a5008094CD14009dD` | Verified, `allowedRouters` set |

Aave PoolAddressesProvider (shared across Polygon/Arbitrum/Optimism): `0xa97684ead0e402dC232d5A977953DF7ECBaB3CDb`

---

# Test Results

Foundry fork tests cover:

- A realistic fork test against live mainnet data (expects a graceful "ei kannattava" revert)
- A `MockRouter`-based forced-profit test proving the contract's own logic
  (approvals, profit check, event emission) works correctly in isolation
- An owner-only access control test

Run with:

```bash
forge test --fork-url $RPC_URL -vvv
