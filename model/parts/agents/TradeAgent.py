import logging

from model.SimState import SimState
log = logging.getLogger('marketagents')

from enforce_typing import enforce_types # type: ignore[import]
import numpy as np
import random
from typing import Tuple, Optional
from .BaseAgent import BaseAgent
from .PoolAgent import PoolAgent
from .util import constants
# from util.constants import POOL_WEIGHT_DT, POOL_WEIGHT_OCEAN
from .web3engine.uniswappool import TokenAmount, Token, Pair
from .web3tools.web3util import toBase18
from enum import Enum

class TradePolicy(Enum):
    TRADE_USD = 1
    TRADE_ETH = 2
    TRADE = 3
    DO_NOTHING = 4

@enforce_types
class TradeAgent(BaseAgent):
    def __init__(self, name: str, USD: float, ETH: float, trade_frequency=random.randrange(30,50), slippage_tolerance=0.005):
        super().__init__(name, USD, ETH)
        self.tradeDone = False
        self.tradeResult = (None, None)
        self.slippage_tolerance = slippage_tolerance
        self.roi = random.randrange(2,5)/100
        self.pool_factor = 2 # factor to the swap fee of the pool to be profitable
        self._s_since_trade = 0
        self._s_between_trade = trade_frequency
        
    def takeStep(self, state, pool_agents):
        self._s_since_trade += state.ss.time_step
    
        if self._doTrade(state):
            self.tradeDone = True
            self._s_since_trade = 0
            white_pool_agent = pool_agents['White Pool']
            grey_pool_agent = pool_agents['Grey Pool']
            (policy, tokenAmount, pool_agent) = self._tradePolicy(state, white_pool_agent, grey_pool_agent)

            if policy == TradePolicy.TRADE_USD:
                # print(f'{self.name} trades with: ', tokenAmountA)
                self.tradeResult = self._trade(state, pool_agent, tokenAmount)
            if policy == TradePolicy.TRADE:
                # print(f'{self.name} swaps with: ', tokenAmountA)
                self.tradeResult = self._trade(state, pool_agent, tokenAmount)
            else:
                pass # DO_NOTHING

    def _doTrade(self, state) -> bool:
        return self._s_since_trade >= self._s_between_trade

    def _trade(self, state, pool_agent: PoolAgent, tokenAmount: TokenAmount) -> Tuple[PoolAgent, TokenAmount]:
        # print("Trader does trade at step: ", state.tick)
        # print("Token: ", tokenAmount)
        outputAmount, new_pair_tokens = pool_agent.takeSwap(tokenAmount)
        new_token0 = new_pair_tokens[0]
        new_token1 = new_pair_tokens[1]
        volume = 0.0
        # adjust balances of wallet
        if new_pair_tokens[0].token.symbol == state.tokenA.symbol:
            new_token0 = new_pair_tokens[0]
            new_token1 = new_pair_tokens[1]
            volume = tokenAmount.amount
            self.payUSD(volume)
            self.receiveETH(outputAmount.amount)
        else:
            new_token0 = new_pair_tokens[1]
            new_token1 = new_pair_tokens[0]
            volume = outputAmount.amount
            self.receiveUSD(volume)
            self.payETH(tokenAmount.amount)
        pool_agent._pool.pair.instantiate(new_token0, new_token1, pool_agent._pool.pair.liquidityToken)
        return (pool_agent, tokenAmount)

    def _tradePolicy(self, state: SimState, white_pool_agent: PoolAgent, grey_pool_agent: PoolAgent) -> Tuple[TradePolicy, TokenAmount, PoolAgent]:
        # trade direction USD -> ETH -> USD
        white_price_usd_to_eth = white_pool_agent._pool.pair.token0Price()
        # print("white_price_usd_to_eth: ", white_price_usd_to_eth)
        grey_price_usd_to_eth = grey_pool_agent._pool.pair.token0Price()
        # print("grey_price_usd_to_eth: ", grey_price_usd_to_eth)
        white_price_eth_to_usd = white_pool_agent._pool.pair.token1Price()
        # print("white_price_usd_to_eth: ", white_price_usd_to_eth)
        grey_price_eth_to_usd = grey_pool_agent._pool.pair.token1Price()
        # print("grey_price_usd_to_eth: ", grey_price_usd_to_eth)
        ratio_usd_to_eth = white_price_usd_to_eth/grey_price_usd_to_eth
        ratio_eth_to_usd = white_price_eth_to_usd/grey_price_eth_to_usd
        
        spread_usd = 0.0
        spread_eth = 0.0
        if ratio_usd_to_eth > 1:
            spread_usd = ratio_usd_to_eth - 1
        if ratio_usd_to_eth <= 1:
            spread_usd = 1 - ratio_usd_to_eth
        if ratio_eth_to_usd > 1:
            spread_eth = 1 - ratio_eth_to_usd
        if ratio_eth_to_usd <= 1:
            spread_eth = 1 - ratio_eth_to_usd

        # print('Ratio: ', ratio_usd_to_eth)
        # print("Spread: ", spread_usd)

        tradeAmount = TokenAmount(state.tokenB, 0.0)
        
        # if I have more USD than ETH worth of USD, trade in USD, else trade for ETH
        # if self.USD() < grey_price_eth_to_usd * self.ETH():
        # hack! I randomly trade in USD and ETH

        if random.random() < 0.5:
            # opportunity to swap ETH from white pool to ETH in grey pool
            if ratio_usd_to_eth <= 1 and spread_usd >= white_pool_agent.pool.swap_fee * self.pool_factor: 
                return self._executeTrade(state.tokenB, white_pool_agent, grey_pool_agent)
            # opportunity to swap ETH from grey pool to ETH in white pool
            if ratio_usd_to_eth > 1 and spread_usd >= grey_pool_agent.pool.swap_fee * self.pool_factor:
                return self._executeTrade(state.tokenB, grey_pool_agent, white_pool_agent)
        else: # trade for ETH
            # opportunity to swap USD from white pool to USD in grey pool
            if ratio_eth_to_usd <= 1 and spread_eth >= white_pool_agent.pool.swap_fee * self.pool_factor: 
                return self._executeTrade(state.tokenA, white_pool_agent, grey_pool_agent)
            # opportunity to swap USD from grey pool to USD in white pool
            if ratio_eth_to_usd > 1 and spread_eth >= grey_pool_agent.pool.swap_fee * self.pool_factor:
                return self._executeTrade(state.tokenA, grey_pool_agent, white_pool_agent)

        return (TradePolicy.DO_NOTHING, tradeAmount, grey_pool_agent)

    def _executeTrade(self, token: Token, pool_agent: PoolAgent, other_pool_agent: PoolAgent) -> Tuple[TradePolicy, TokenAmount, PoolAgent]:

        tradeAmount = TokenAmount(token, 0.0)

        trade_size_eth = np.random.lognormal(1.0, 1.0) # default grey pool trade size
        if 'White Pool' in pool_agent.name:
            trade_size_eth = np.random.lognormal(0.1, 1.0)

        trade_size_usd = np.random.lognormal(8.0, 1.0)  # default grey pool trade size
        if 'White Pool' in pool_agent.name:
            trade_size_usd = np.random.lognormal(8.0, 1.0)

        if token.symbol == "ETH":
            tradeAmount = TokenAmount(token, trade_size_eth)
        else:
            tradeAmount = TokenAmount(token, trade_size_usd)
        # print("Trade token: ", tradeAmount)
        
        (outputAmount, slippage) = self._getSlippage(pool_agent,tradeAmount)
        # print("Slippage: ", slippage)
        if slippage <= self.slippage_tolerance:
            profit = self._getProfit(pool_agent, other_pool_agent, tradeAmount)
            # print("Profit: ", profit)
            # print("Trade amount: ", tradeAmount)
            if profit >= self.roi:
                return (TradePolicy.TRADE, tradeAmount, pool_agent)
        else:
            return (TradePolicy.DO_NOTHING, tradeAmount, pool_agent)
        return (TradePolicy.DO_NOTHING, tradeAmount, pool_agent)

    def _getProfit(self, pool_agent: PoolAgent, other_pool_agent: PoolAgent, inputAmount: TokenAmount) -> float:
        (outputAmount, slippage) = self._getSlippage(pool_agent, inputAmount)
        (outputAmount2, slippage) = self._getSlippage(other_pool_agent, outputAmount)
        return (outputAmount2.amount - inputAmount.amount)/inputAmount.amount

    def _getSlippage(self, pool_agent: PoolAgent, inputAmount: TokenAmount) -> Tuple[TokenAmount, float]:
        slippage = 0.0
        pair = pool_agent._pool.pair
        token0 = pair.token0
        outputAmount, new_pair_tokens = pool_agent.takeSwap(inputAmount)
        new_pair = Pair(new_pair_tokens[0], new_pair_tokens[1])
        new_price_ratio = 0.0
        if inputAmount.token.symbol == token0.token.symbol:
            # USD
            old_price_ratio = pair.token1Price()
            if new_pair_tokens[0].token.symbol == token0.token.symbol:
                new_price_ratio = new_pair.token1Price()
            else:
                new_price_ratio = new_pair.token0Price()
            slippage = 1 - old_price_ratio/new_price_ratio if new_price_ratio != 0 else 1
        else:
            # ETH
            old_price_ratio = pair.token0Price()
            if new_pair_tokens[0].token.symbol == token0.token.symbol:
                new_price_ratio = new_pair.token0Price()
            else:
                new_price_ratio = new_pair.token1Price()
            # print("old_price_ratio: ", old_price_ratio)
            # print("new_price_ratio: ", new_price_ratio)        
            slippage = 1 - old_price_ratio/new_price_ratio if new_price_ratio != 0 else 1
        return (outputAmount, slippage)