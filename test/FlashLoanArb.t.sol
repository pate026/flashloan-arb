// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "forge-std/Test.sol";
import "../src/FlashLoanArb.sol";
import "./mocks/MockPoolAddressesProvider.sol";

contract FlashLoanArbTest is Test {
    FlashLoanArb arb;
    MockPoolAddressesProvider provider;

    function setUp() public {
        provider = new MockPoolAddressesProvider(address(0x1234));
        arb = new FlashLoanArb(address(provider));
    }

    function testDeploy() public view {
        assertTrue(address(arb) != address(0));
    }
}
