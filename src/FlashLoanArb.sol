// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {Ownable2Step} from "openzeppelin-contracts/contracts/access/Ownable2Step.sol";
import {Ownable} from "openzeppelin-contracts/contracts/access/Ownable.sol";
import {Pausable} from "openzeppelin-contracts/contracts/utils/Pausable.sol";
import {ReentrancyGuard} from "openzeppelin-contracts/contracts/utils/ReentrancyGuard.sol";
import {SafeERC20} from "openzeppelin-contracts/contracts/token/ERC20/utils/SafeERC20.sol";
import {IERC20} from "openzeppelin-contracts/contracts/token/ERC20/IERC20.sol";

import {IPool} from "aave-v3-core/contracts/interfaces/IPool.sol";

import {ISwapRouter} from "v3-periphery/interfaces/ISwapRouter.sol";

/// @title FlashLoanArb
/// @notice Production-grade Flash Loan Arbitrage Contract
contract FlashLoanArb is Ownable2Step, Pausable, ReentrancyGuard {
    using SafeERC20 for IERC20;

    /// @notice Aave Pool
    IPool public immutable aavePool;

    /// @notice Uniswap V3 Router
    ISwapRouter public immutable swapRouter;

    event FlashLoanRequested(address asset, uint256 amount);
    event ArbitrageExecuted(address tokenIn, address tokenOut, uint256 profit);
    event EmergencyWithdraw(address token, uint256 amount);

    constructor(address initialOwner, address pool, address router) Ownable(initialOwner) {
        aavePool = IPool(pool);
        swapRouter = ISwapRouter(router);
    }
}
