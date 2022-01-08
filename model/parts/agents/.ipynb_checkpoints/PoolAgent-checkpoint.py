import logging
log = logging.getLogger('poolagents')

from enforce_typing import enforce_types # type: ignore[import]
import random

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
     
        
    def takeLiquidity(tokenAmount0: TokenAmount, tokenAmount1: TokenAmount) -> TokenAmount:
        pair = self._pool.pair
        
        liquidity = pair.getLiquidityMinted(pair.liquidityToken, tokenAmount0, tokenAmount1)
        new_amount0 = pair.token0.token.amount + tokenAmount0.amount
        new_amount1 = pair.token1.token.amount + tokenAmount1.amount
        
        new_pair= Pair(TokenAmount(pair.token0.token, new_amount0), TokenAmount(pair.token1.token, new_amount1))
        
        # should we do this?
        new_pair.txCount = pair.txCount + 1
        
        new_pair.liquidityToken = TokenAmount(pair.liquidityToken.token, pair.liquidityToken.amount + liquidity.amount) 
        self._pool.pair = new_pair
        return liquidity
        
    def takeSwap(inputAmount: TokenAmount) -> TokenAmount:
        pair = self._pool.pair
        
        outputAmount, new_pair = pair.getOutputAmount(inputAmount)
        new_pair.txCount = pair.txCount + 1
        self._pool.pair = new_pair
        return outputAmount
                           
    def takeStep(self, state):
        #it's a smart contract robot, it doesn't initiate anything itself
        pass
        
