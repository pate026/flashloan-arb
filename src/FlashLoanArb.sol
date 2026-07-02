// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "aave-v3-core/contracts/flashloan/base/FlashLoanSimpleReceiverBase.sol";
import "aave-v3-core/contracts/interfaces/IPoolAddressesProvider.sol";
import "openzeppelin-contracts/contracts/access/Ownable.sol";
import "openzeppelin-contracts/contracts/token/ERC20/IERC20.sol";

contract FlashLoanArb is FlashLoanSimpleReceiverBase, Ownable {
    struct ArbParams {
        address dexA;
        address dexB;
        address tokenIn;
        address tokenOut;
        uint256 minProfit;
    }

    event FlashLoanRequested(address indexed asset, uint256 amount);
    event FlashLoanExecuted(address indexed asset, uint256 amount, uint256 premium);

    constructor(address provider) FlashLoanSimpleReceiverBase(IPoolAddressesProvider(provider)) Ownable(msg.sender) {}

    function requestFlashLoan(address asset, uint256 amount, bytes calldata params) external onlyOwner {
        emit FlashLoanRequested(asset, amount);

        POOL.flashLoanSimple(address(this), asset, amount, params, 0);
    }

    function executeOperation(address asset, uint256 amount, uint256 premium, address initiator, bytes calldata params)
        external
        override
        returns (bool)
    {
        require(msg.sender == address(POOL), "Caller is not Aave Pool");
        require(initiator == address(this), "Invalid initiator");

        ArbParams memory arb = abi.decode(params, (ArbParams));
        arb;

        emit FlashLoanExecuted(asset, amount, premium);

        uint256 amountOwed = amount + premium;
        IERC20(asset).approve(address(POOL), amountOwed);

        return true;
    }
}
