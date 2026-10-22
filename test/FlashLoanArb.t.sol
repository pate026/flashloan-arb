// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {Test, console} from "forge-std/Test.sol";
import {FlashLoanArb} from "../src/FlashLoanArb.sol";
import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";

contract FlashLoanArbForkTest is Test {
    address constant AAVE_PROVIDER = 0xa97684ead0e402dC232d5A977953DF7ECBaB3CDb;
    address constant USDC = 0xaf88d065e77c8cC2239327C5EDb3A432268e5831; // Arbitrum native USDC
    address constant WETH = 0x82aF49447D8a07e3bd95BD0d56f35241523fBab1; // Arbitrum WETH
    address constant UNIV3_ROUTER = 0xE592427A0AEce92De3Edee1F18E0157C05861564;

    FlashLoanArb arb;

    function setUp() public {
        arb = new FlashLoanArb(AAVE_PROVIDER);
        arb.setRouterAllowed(UNIV3_ROUTER, true);
    }

    function test_arbitrage_USDC_WETH() public {
        uint256 loanAmount = 10_000e6;

        FlashLoanArb.ArbParams memory p = FlashLoanArb.ArbParams({
            routerBuy: UNIV3_ROUTER,
            routerSell: UNIV3_ROUTER,
            tokenMid: WETH,
            feeBuy: 500,
            feeSell: 3000,
            minProfit: 1
        });

        try arb.requestFlashLoan(USDC, loanAmount, p) {
            uint256 profit = IERC20(USDC).balanceOf(address(arb));
            console.log("Arbitraasi KANNATTAVA. USDC-saldo:", profit);
            assertGt(profit, 0, "voittoa piti jaada");
        } catch Error(string memory reason) {
            console.log("Revert (odotettu):", reason);
            assertEq(reason, "ei kannattava", "vaara revert-syy");
        }
    }

    function test_onlyOwner_canRequest() public {
        FlashLoanArb.ArbParams memory p = FlashLoanArb.ArbParams({
            routerBuy: UNIV3_ROUTER,
            routerSell: UNIV3_ROUTER,
            tokenMid: WETH,
            feeBuy: 500,
            feeSell: 3000,
            minProfit: 1
        });

        vm.prank(address(0xBEEF));
        vm.expectRevert();
        arb.requestFlashLoan(USDC, 1_000e6, p);
    }

    function test_highMinProfit_reverts() public {
        uint256 loanAmount = 10_000e6;

        FlashLoanArb.ArbParams memory p = FlashLoanArb.ArbParams({
            routerBuy: UNIV3_ROUTER,
            routerSell: UNIV3_ROUTER,
            tokenMid: WETH,
            feeBuy: 500,
            feeSell: 3000,
            minProfit: 1_000_000e6
        });

        vm.expectRevert(bytes("ei kannattava"));
        arb.requestFlashLoan(USDC, loanAmount, p);
    }
}
