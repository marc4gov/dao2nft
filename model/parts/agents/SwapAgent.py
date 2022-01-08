import logging

from model.SimState import SimState
log = logging.getLogger('marketagents')

from enforce_typing import enforce_types # type: ignore[import]
import random
from typing import Tuple, Optional
from .TradeAgent import TradeAgent, TradePolicy
from .PoolAgent import PoolAgent
from .util import constants
# from util.constants import POOL_WEIGHT_DT, POOL_WEIGHT_OCEAN
from .web3engine.uniswappool import TokenAmount, Pair
from .web3tools.web3util import toBase18
from enum import Enum


@enforce_types
class SwapAgent(TradeAgent):
    def __init__(self, name: str, USD: float, ETH: float, trade_frequency=random.randrange(30,50), slippage_tolerance=0.005):
        super().__init__(name, USD, ETH, trade_frequency, slippage_tolerance)
        self.roi = random.randrange(2,5)/100
        self._s_between_trade = random.randrange(4,6) # magic number


    def _tradePolicy(self, state: SimState, white_pool_agent: PoolAgent, grey_pool_agent: PoolAgent) -> Tuple[TradePolicy, TokenAmount, PoolAgent]:
        my_usd_trade_size = self.USD() * random.randrange(30,50)/100
        my_eth_trade_size = self.ETH() * random.randrange(30,50)/100
        
        tradeAmount = TokenAmount(state.tokenA, my_usd_trade_size)
        if self.USD() < my_usd_trade_size: return (TradePolicy.DO_NOTHING, tradeAmount, white_pool_agent) 

        if random.random() < 0.5:
            tradeAmount = TokenAmount(state.tokenB, my_eth_trade_size)
            if self.ETH() < my_eth_trade_size: return (TradePolicy.DO_NOTHING, tradeAmount, white_pool_agent)

        (outputAmount_white, slippage_white) = self._getSlippage(white_pool_agent,tradeAmount)
        (outputAmount_grey, slippage_grey) = self._getSlippage(grey_pool_agent,tradeAmount)
        if slippage_white <= slippage_grey:
            return (TradePolicy.TRADE, tradeAmount, white_pool_agent)
        else:
            return (TradePolicy.TRADE, tradeAmount, grey_pool_agent)


