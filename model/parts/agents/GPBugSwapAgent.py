import logging

from model.SimState import SimState
log = logging.getLogger('marketagents')

from enforce_typing import enforce_types # type: ignore[import]
import numpy as np
import random
from typing import Tuple, Optional
from .TradeAgent import TradePolicy
from .GPSwapAgent import GPSwapAgent
from .PoolAgent import PoolAgent
from .util import constants
# from util.constants import POOL_WEIGHT_DT, POOL_WEIGHT_OCEAN
from .web3engine.uniswappool import TokenAmount, Pair
from .web3tools.web3util import toBase18


@enforce_types
class GPBugSwapAgent(GPSwapAgent):
    def __init__(self, name: str, USD: float, ETH: float, trade_frequency=random.randrange(30,50), slippage_tolerance=0.005):
        super().__init__(name, USD, ETH, trade_frequency, slippage_tolerance)
        self._s_between_trade = random.randrange(30,35) # magic number

    def _tradePolicy(self, state: SimState, white_pool_agent: PoolAgent, grey_pool_agent: PoolAgent) -> Tuple[TradePolicy, TokenAmount, PoolAgent]:
        my_usd_trade_size = np.random.lognormal(5, 1.0)
        my_eth_trade_size = np.random.lognormal(1, 1.0)

        if state.tick > 100 and state.tick < 1000:
            my_eth_trade_size = self.ETH() * 0.9

        tradeAmount = TokenAmount(state.tokenA, my_usd_trade_size)

        if self.USD() < my_usd_trade_size: return (TradePolicy.DO_NOTHING, tradeAmount, grey_pool_agent) 
        if random.random() < 0.7:
            tradeAmount = TokenAmount(state.tokenB, my_eth_trade_size)
            if self.ETH() < my_eth_trade_size: return (TradePolicy.DO_NOTHING, tradeAmount, grey_pool_agent)

        (outputAmount_white, slippage_grey) = self._getSlippage(grey_pool_agent,tradeAmount)
        while slippage_grey > 0.02:
            tradeAmount.amount = 0.5 * tradeAmount.amount
            (outputAmount_white, slippage_grey) = self._getSlippage(grey_pool_agent,tradeAmount)
        return (TradePolicy.TRADE, tradeAmount, grey_pool_agent)


