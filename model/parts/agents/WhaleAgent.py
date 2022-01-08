import logging
log = logging.getLogger('marketagents')

from enforce_typing import enforce_types # type: ignore[import]
import random
from typing import Tuple, Optional
from .LiquidityProviderAgent import LiquidityProviderAgent, LPPolicy
from .PoolAgent import PoolAgent

from .web3engine.uniswappool import Token, TokenAmount, Pair
# from web3engine import bfactory, bpool, btoken, datatoken, dtfactory
# from web3tools.web3util import toBase18
from .util import constants

@enforce_types
class WhaleAgent(LiquidityProviderAgent):
    """Provides and burns liquidity in huge amounts"""
    
    def __init__(self, name: str, USD: float, ETH: float, white: Token, grey: Token):
        super().__init__(name, USD, ETH, white, grey)
        self._s_between_lp = random.randrange(500, 600) #magic number

    def _lpPolicy(self, state, white_pool_agent: PoolAgent, grey_pool_agent: PoolAgent) -> Tuple[LPPolicy, TokenAmount, PoolAgent]:

        my_reserve_usd = self.USD()
        my_reserve_eth = self.ETH()
        my_liquidity = self.liquidityToken

        white_reserve_usd = white_pool_agent.pool.pair.reserve0().amount
        white_reserve_eth = white_pool_agent.pool.pair.reserve1().amount
        grey_reserve_usd = grey_pool_agent.pool.pair.reserve0().amount
        grey_reserve_eth = grey_pool_agent.pool.pair.reserve1().amount
        
        ratio_wp = my_reserve_usd/white_reserve_usd if white_reserve_usd != 0 else 0
        ratio_gp = my_reserve_usd/grey_reserve_usd if grey_reserve_usd != 0 else 0
        print("ratio wp: " , ratio_wp)
        print("ratio gp: ", ratio_gp)
        tokenAmount = TokenAmount(state.tokenA, 0.0)
        # adjust to rational amounts
        if ratio_wp >= ratio_gp and ratio_wp >= 0.5:
            tokenAmount.amount = my_reserve_usd * random.randrange(50,70)/100
            print("Whale: ", tokenAmount)
            return (LPPolicy.PROVIDE, tokenAmount, white_pool_agent)
        if ratio_gp > ratio_wp and ratio_gp > 0.5:
            tokenAmount.amount = my_reserve_usd * random.randrange(50,70)/100
            print("Whale: ", tokenAmount)
            return (LPPolicy.PROVIDE, tokenAmount, grey_pool_agent)

        return (LPPolicy.DO_NOTHING, tokenAmount, grey_pool_agent)
        
        
        
