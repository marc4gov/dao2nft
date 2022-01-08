import logging
log = logging.getLogger('poolagents')

from enforce_typing import enforce_types # type: ignore[import]
import random

from typing import Tuple
from .BaseAgent import BaseAgent
from .web3engine.uniswappool import TokenAmount, Pair, UniswapPool
from .web3tools.web3util import toBase18

            
@enforce_types
class PoolAgent(BaseAgent):    
    def __init__(self, name: str, pool: UniswapPool):
        super().__init__(name, USD=0.0, ETH=0.0)
        self._pool = pool

    @property
    def pool(self) -> UniswapPool:
        return self._pool
        
    def takeLiquidity(self, tokenAmount0: TokenAmount, tokenAmount1: TokenAmount) -> TokenAmount:
        pair = self._pool.pair
        
        return pair.getLiquidityMinted(pair.liquidityToken, tokenAmount0, tokenAmount1)
        
    def takeSwap(self, inputAmount: TokenAmount) -> Tuple[TokenAmount, Tuple[TokenAmount, TokenAmount]]:
        pair = self._pool.pair
        return pair.getOutputAmount(inputAmount)
                           
    def takeStep(self, state):
        #it's a smart contract robot, it doesn't initiate anything itself
        pass
        
