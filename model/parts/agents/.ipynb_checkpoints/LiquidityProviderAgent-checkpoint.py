import logging
log = logging.getLogger('marketagents')

from enforce_typing import enforce_types # type: ignore[import]
import random

from .BaseAgent import BaseAgent
# from web3engine import bfactory, bpool, btoken, datatoken, dtfactory
# from web3tools.web3util import toBase18
from .util import constants
                    
@enforce_types
class LiquidityProviderAgent(BaseAgent):
    """Provides and removes liquidity"""
    
    def __init__(self, name: str, USD: float, OCEAN: float):
        super().__init__(name, USD, OCEAN)

        self._s_since_lp = 0
        self._s_between_lp = 8 * constants.S_PER_HOUR #magic number
        
    def takeStep(self, state):
        self._s_since_lp += state.ss.time_step

        if self._doLPAction(state):
            self._s_since_speculate = 0
            self._lpAction(state)

    def _doLPAction(self, state):
        pool_agents = state.agents.filterToPool().values()
        if not pool_agents:
            return False
        else:
            return self._s_since_speculate >= self._s_between_speculates

    def _lpAction(self, state):
        pool_agents = state.agents.filterToPool().values()
        assert pool_agents, "need pools to be able to provide liquidity"
        
        pool = random.choice(list(pool_agents)).pool
        BPT = self.BPT(pool)
        
        if BPT > 0.0 and random.random() < 0.50: #magic number
            BPT_sell = 0.10 * BPT #magic number
            self.unstakeOCEAN(BPT_sell, pool)
            
        else:
            OCEAN_stake = 0.10 * self.OCEAN() #magic number
            self.stakeOCEAN(OCEAN_stake, pool)
        
            
