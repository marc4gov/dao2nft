import logging
log = logging.getLogger('marketagents')

from enforce_typing import enforce_types # type: ignore[import]
import random

from .BaseAgent import BaseAgent
from .PoolAgent import PoolAgent
from .util import constants
# from util.constants import POOL_WEIGHT_DT, POOL_WEIGHT_OCEAN
from .web3engine.uniswappool import TokenAmount, Pair, UniswapPool
from .web3tools.web3util import toBase18
        
@enforce_types
class TradeAgent(BaseAgent):
    def __init__(self, name: str, USD: float, ETH: float):
        super().__init__(name, USD, ETH)
        
        self._s_since_trade = 0
        self._s_between_trade = 3 * constants.S_PER_DAY #magic number
        
    def takeStep(self, state) -> None:
        self._s_since_trade += state.ss.time_step
    
        if self._doTrade(state):
            self._s_since_trade = 0
            self._trade(state)


    def _doTrade(self, state) -> bool:
        return self._s_since_trade >= self._s_between_trade

    def _trade(self, state):
        """Choose what pool to unstake and by how much. Then do the action."""
        pool_agents = state.agents.filterByNonzeroStake(self)
        pool_agent = random.choice(list(pool_agents.values()))


