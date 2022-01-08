import logging
log = logging.getLogger('marketagents')

from enforce_typing import enforce_types # type: ignore[import]
import random
from typing import Tuple, Optional
from .BaseAgent import BaseAgent
from .PoolAgent import PoolAgent

from .web3engine.uniswappool import Token, TokenAmount, Pair
# from web3engine import bfactory, bpool, btoken, datatoken, dtfactory
# from web3tools.web3util import toBase18
from .util import constants

from enum import Enum

class LPPolicy(Enum):
    PROVIDE = 1
    BURN = 2
    DO_NOTHING = 3

@enforce_types
class LiquidityProviderAgent(BaseAgent):
    """Provides and burns liquidity"""
    
    def __init__(self, name: str, USD: float, ETH: float, white: Token, grey: Token):
        super().__init__(name, USD, ETH)
        self.liquidityToken = {'White Pool': TokenAmount(white, 0.0), 'Grey Pool': TokenAmount(grey, 0.0)}
        self.lpDone = False
        self.lpResult = (None, None)
        self.roi = random.randrange(10,20)/100
        self.treshold = 10000

        self._s_since_lp = 0
        self._s_between_lp = random.randrange(20, 30) #magic number
        
    def takeStep(self, state, pool_agents):
        self._s_since_lp += state.ss.time_step

        if self._doLPAction(state):
            self.lpDone = True
            self._s_since_lp = 0
    
            white_pool_agent = pool_agents['White Pool']
            grey_pool_agent = pool_agents['Grey Pool']
            
            (policy, tokenAmountA, pool_agent) = self._lpPolicy(state, white_pool_agent, grey_pool_agent)

            tokenAmountB = TokenAmount(pool_agent._pool.pair.token1.token, pool_agent._pool.pair.token0Price() * tokenAmountA.amount)
            if policy == LPPolicy.PROVIDE:
                self.lpResult = self._provide(state, pool_agent, tokenAmountA, tokenAmountB)
            if policy == LPPolicy.BURN:
                self.lpResult = self._burn(state, pool_agent, tokenAmountA)
            else:
                pass # DO_NOTHING


    def _doLPAction(self, state):
        return self._s_since_lp >= self._s_between_lp

    def _provide(self, state, pool_agent: PoolAgent, tokenAmountA : TokenAmount, tokenAmountB: TokenAmount) -> Tuple[PoolAgent, float]:
        # print("LP agent provides liquidity at step: ", state.tick)

        # top up liquidity share
        liquidityMinted = pool_agent.takeLiquidity(tokenAmountA, tokenAmountB)
        self.liquidityToken[pool_agent.name].amount += liquidityMinted.amount
        
        # adjust balances of agent wallet
        self.payUSD(tokenAmountA.amount)
        self.payETH(tokenAmountB.amount)

        pool_agent._pool.pair.update(tokenAmountA.amount, tokenAmountB.amount, liquidityMinted.amount)

        return (pool_agent, liquidityMinted.amount)

    def _burn(self, state, pool_agent, tokenAmountA) -> Tuple[PoolAgent, float]:
        print("LP agent burns liquidity at step: ", state.tick)
        
        pair = pool_agent._pool.pair
        pool_agent_liquidity = pair.liquidityToken
        pool_volume_usd = pair.token0.amount

        volume_to_burn = tokenAmountA.amount
        share = volume_to_burn/pool_volume_usd
        usd_share = share * pair.token0.amount
        eth_share = share * pair.token1.amount
        # adjust balances of agent wallet
        self.receiveUSD(usd_share)
        self.receiveETH(eth_share)

        # burn the liquidity tokens
        burned_liquidity = share * pool_agent_liquidity.amount
    
        self.liquidityToken[pool_agent.name].amount -= burned_liquidity

        # update the new pool balance and liquidity
        pool_agent._pool.pair.update(- usd_share, - eth_share, - burned_liquidity)

        return (pool_agent, burned_liquidity)


    def _lpPolicy(self, state, white_pool_agent: PoolAgent, grey_pool_agent: PoolAgent) -> Tuple[LPPolicy, TokenAmount, PoolAgent]:
        days_elapsed = state.tick/(state.ss.time_step * constants.S_PER_DAY)
        expected_fees_usd_white_per_year = 365 * white_pool_agent._pool.swap_fee * state.white_pool_volume_USD/days_elapsed
        expected_fees_usd_grey_per_year = 365 * grey_pool_agent._pool.swap_fee * state.grey_pool_volume_USD/days_elapsed
        expected_fees_eth_white_per_year = 365 * white_pool_agent._pool.swap_fee * state.white_pool_volume_ETH/days_elapsed
        expected_fees_eth_grey_per_year = 365 * grey_pool_agent._pool.swap_fee * state.grey_pool_volume_ETH/days_elapsed

        my_volume_usd = self._wallet.USD()
        my_volume_eth = self._wallet.ETH()
        my_liquidity = self.liquidityToken

        roi_white_usd = my_volume_usd/expected_fees_usd_white_per_year if expected_fees_usd_white_per_year != 0 else 0
        roi_white_eth = my_volume_eth/expected_fees_eth_white_per_year if expected_fees_eth_white_per_year != 0 else 0
        roi_white = roi_white_eth + roi_white_usd

        # print("roi_white" , roi_white)
        roi_grey_usd = my_volume_usd/expected_fees_usd_grey_per_year if expected_fees_usd_grey_per_year != 0 else 0
        roi_grey_eth = my_volume_usd/expected_fees_eth_grey_per_year if expected_fees_eth_grey_per_year != 0 else 0
        roi_grey = roi_grey_eth + roi_grey_usd
        # print("roi_grey" , roi_grey)



        amount = TokenAmount(state.tokenA, my_volume_usd * random.randrange(15,20)/100)
        # if max(roi_white, roi_grey) >= self.roi and my_volume_usd > self.treshold:

        # hack! as long as I have funds, I provide liquidity
        if my_volume_usd > self.treshold:
            if roi_white > roi_grey:
                return (LPPolicy.PROVIDE, amount, white_pool_agent)
            else:
                return (LPPolicy.PROVIDE, amount, grey_pool_agent)
        # if min(roi_white, roi_grey) < self.roi:
        else:
            if roi_white < roi_grey and my_liquidity[white_pool_agent.name].amount < self._defineLiquidityTreshold(white_pool_agent, 0.80):
                return (LPPolicy.BURN, amount, white_pool_agent)
            if roi_white >= roi_grey and my_liquidity[grey_pool_agent.name].amount < self._defineLiquidityTreshold(grey_pool_agent, 0.80):
                return (LPPolicy.BURN, amount, grey_pool_agent)
        return (LPPolicy.DO_NOTHING, amount, grey_pool_agent)

    def _defineLiquidityTreshold(self, pool_agent, percentage) -> float:
        pair = pool_agent._pool.pair
        pool_agent_liquidity = pair.liquidityToken
        pool_volume_usd = pair.token0.amount
        pool_share = self.liquidityToken[pool_agent.name]
        share_in_usd = pool_volume_usd * pool_share.amount/pool_agent_liquidity.amount
        return share_in_usd * percentage
        
        
        
