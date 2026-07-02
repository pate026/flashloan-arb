// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// ─────────────────────────────────────────────────────────────────────────────
// OpenZeppelin
// ─────────────────────────────────────────────────────────────────────────────

import {Ownable2Step} from "@openzeppelin/contracts/access/Ownable2Step.sol";
import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";
import {Pausable} from "@openzeppelin/contracts/utils/Pausable.sol";
import {ReentrancyGuard} from "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
import {SafeERC20} from "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";

// ─────────────────────────────────────────────────────────────────────────────
// Aave
// ─────────────────────────────────────────────────────────────────────────────

import {IPool} from "aave-v3-core/contracts/interfaces/IPool.sol";

// ─────────────────────────────────────────────────────────────────────────────
// Uniswap V3
// ─────────────────────────────────────────────────────────────────────────────

import {ISwapRouter} from "v3-periphery/interfaces/ISwapRouter.sol";

/// @title FlashLoanArb
/// @notice Production-grade Flash Loan Arbitrage contract (under development)
contract FlashLoanArb is Ownable2Step, Pausable, ReentrancyGuard {
    using SafeERC20 for IERC20;

    /// @notice Aave Pool
    IPool public immutable aavePool;

    /// @notice Primary swap router
    ISwapRouter public immutable swapRouter;

    constructor(
        address initialOwner,
        address pool,
        address router
    ) Ownable(initialOwner) {
        aavePool = IPool(pool);
        swapRouter = ISwapRouter(router);
    }
}
