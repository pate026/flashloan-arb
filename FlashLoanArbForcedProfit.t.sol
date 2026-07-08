// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {Test, console} from "forge-std/Test.sol";
import {FlashLoanArb} from "../src/FlashLoanArb.sol";
import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";

/**
 * Mock-router, joka simuloi ISwapRouterV3.exactInputSingle-kutsua
 * KIINTEALLA, ETUKATEEN MAARITELLYLLA vaihtokurssilla.
 */
contract MockRouter {
    mapping(address => mapping(address => uint256)) public rate;

    function setRate(address tokenIn, address tokenOut, uint256 rateScaled) external {
        rate[tokenIn][tokenOut] = rateScaled;
    }

    struct ExactInputSingleParams {
        address tokenIn;
        address tokenOut;
        uint24 fee;
        address recipient;
        uint256 deadline;
        uint256 amountIn;
        uint256 amountOutMinimum;
        uint160 sqrtPriceLimitX96;
    }

    function exactInputSingle(ExactInputSingleParams calldata params)
        external
        returns (uint256 amountOut)
    {
        uint256 r = rate[params.tokenIn][params.tokenOut];
        require(r > 0, "rate ei asetettu");

        IERC20(params.tokenIn).transferFrom(msg.sender, address(this), params.amountIn);

        amountOut = (params.amountIn * r) / 1e18;
        require(amountOut >= params.amountOutMinimum, "slippage");

        IERC20(params.tokenOut).transfer(params.recipient, amountOut);
    }
}

contract FlashLoanArbForcedProfitTest is Test {
    address constant AAVE_PROVIDER = 0xa97684ead0e402dC232d5A977953DF7ECBaB3CDb;
    address constant USDC = 0xaf88d065e77c8cC2239327C5EDb3A432268e5831; // Arbitrum native USDC
    address constant WETH = 0x82aF49447D8a07e3bd95BD0d56f35241523fBab1; // Arbitrum WETH

    FlashLoanArb arb;
    MockRouter mockRouter;

    function setUp() public {
        arb = new FlashLoanArb(AAVE_PROVIDER);
        mockRouter = new MockRouter();
        arb.setRouterAllowed(address(mockRouter), true);

        deal(WETH, address(mockRouter), 1_000e18);
        deal(USDC, address(mockRouter), 10_000_000e6);
    }

    function test_forcedProfitableArbitrage() public {
        uint256 loanAmount = 10_000e6;

        mockRouter.setRate(USDC, WETH, 5e26);
        mockRouter.setRate(WETH, USDC, 2020e6);

        FlashLoanArb.ArbParams memory p = FlashLoanArb.ArbParams({
            routerBuy: address(mockRouter),
            routerSell: address(mockRouter),
            tokenMid: WETH,
            feeBuy: 500,
            feeSell: 3000,
            minProfit: 1e6
        });

        assertEq(IERC20(USDC).balanceOf(address(arb)), 0);

        arb.requestFlashLoan(USDC, loanAmount, p);

        uint256 finalBalance = IERC20(USDC).balanceOf(address(arb));
        console.log("Kontraktin USDC-saldo arbitraasin jalkeen:", finalBalance);

        assertGt(finalBalance, 0, "voittoa olisi pitanyt jaada kontraktille");
    }

    function test_forcedProfitableArbitrage_emitsEvent() public {
        uint256 loanAmount = 10_000e6;

        mockRouter.setRate(USDC, WETH, 5e26);
        mockRouter.setRate(WETH, USDC, 2020e6);

        FlashLoanArb.ArbParams memory p = FlashLoanArb.ArbParams({
            routerBuy: address(mockRouter),
            routerSell: address(mockRouter),
            tokenMid: WETH,
            feeBuy: 500,
            feeSell: 3000,
            minProfit: 1e6
        });

        vm.expectEmit(true, false, false, false);
        emit FlashLoanArb.ArbExecuted(USDC, loanAmount, 0);

        arb.requestFlashLoan(USDC, loanAmount, p);
    }
}
