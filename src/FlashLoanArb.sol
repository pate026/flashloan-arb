// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

contract FlashLoanArb {
    address public immutable pool;

    constructor(address _pool) {
        require(_pool != address(0), "Invalid pool");
        pool = _pool;
    }

    function getPool() external view returns (address) {
        return pool;
    }
}
