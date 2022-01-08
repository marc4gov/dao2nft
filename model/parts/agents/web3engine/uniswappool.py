from enforce_typing import enforce_types # type: ignore[import]
from typing import Tuple, List
import requests
import uuid
import math

from ...agents.AgentWallet import AgentWallet

from enum import Enum

class TradeType(Enum):
    EXACT_INPUT = 1
    EXACT_OUTPUT = 2

class Rounding(Enum):
    ROUND_DOWN = 1
    ROUND_HALF_UP = 2
    ROUND_UP = 3

    
SWAP_FEE = 0.003
# from web3tools import web3util, web3wallet
# from .btoken import BToken


class Token():
    def __init__(self, token_id: str, symbol: str, name: str):
        self.token_id = token_id
        self.symbol = symbol
        self.name = name

class TokenAmount():
    def __init__(self, token: Token, amount: float):
        self.token = token
        self.amount = amount

    def __str__(self) -> str:
        s = []
        s += ["TokenAmount - "]
        s += [f"{self.token.symbol}: {self.amount}"]
        return "\n".join(s)  
        
class Pair():
    def __init__(self, token0: TokenAmount, token1: TokenAmount):
        self.token0 = token0
        self.token1 = token1
        liquidity = math.sqrt(token0.amount*token1.amount)
        self.liquidityToken = TokenAmount(Token(uuid.uuid4(), 'UNI-V2', 'Uniswap V2'), liquidity)
        self.txCount = 1
    
    def update(self, delta0: float, delta1: float, deltaL:float):
        self.token0.amount += delta0
        self.token1.amount += delta1
        self.liquidityToken.amount += deltaL

    def instantiate(self, token0: TokenAmount, token1: TokenAmount, liquidityAmount: TokenAmount):
        self.token0 = token0
        self.token1 = token1
        self.liquidityToken = liquidityAmount

    def token0Price(self) -> float:
        return self.token1.amount/self.token0.amount
    
    def token1Price(self) -> float:
        return self.token0.amount/self.token1.amount
    
    def reserve0(self) -> TokenAmount:
        return self.token0
    
    def reserve1(self) -> TokenAmount:
        return self.token1
    
    def reserveOf(self, token: Token) -> TokenAmount:
        if token.symbol == self.token0.token.symbol:
            return self.token0
        else:
            return self.token1
    
    def getOutputAmount(self, inputA: TokenAmount) -> Tuple[TokenAmount, Tuple[TokenAmount, TokenAmount]]:
        
        inputToken = self.reserveOf(inputA.token)
        # print("Input: ", inputToken)
        inputReserve = inputToken.amount
        # print("inputReserve: ", inputReserve)
        outputToken = None
        if inputA.token.symbol == self.token1.token.symbol:
            outputToken = self.token0
        else:
            outputToken = self.token1
        # print("Output: ", outputToken)
        outputReserve = outputToken.amount
        # print("outputReserve: ", outputReserve)
        k = inputReserve * outputReserve
        gamma = 1 - SWAP_FEE
        # Transactions must satisfy (Rα − ∆α)(Rβ + γ∆β) = k
        # (Rα − ∆α) = k/(Rβ + γ∆β) => ∆α = Rα - k/(Rβ + γ∆β)
        output = outputReserve - k/(inputReserve + gamma*inputA.amount)
        # print("outputAmount: ", output)
        return (TokenAmount(outputToken.token, output), [TokenAmount(inputA.token, inputReserve + inputA.amount), TokenAmount(outputToken.token, outputReserve - output)])

    def getInputAmount(self, outputA: TokenAmount) -> Tuple[TokenAmount, Tuple[TokenAmount, TokenAmount]]:
        outputReserve = self.reserveOf(outputA.token).amount
        inputToken = None
        if outputA.token.symbol == self.token0.token.symbol:
            inputToken = self.token1
        else:
            inputToken = self.token0
        inputReserve = inputToken.amount
        k = inputReserve * outputReserve
        gamma = 1 - SWAP_FEE
        
        # Transactions must satisfy (Rα − ∆α)(Rβ + γ∆β) = k
        # (Rβ + γ∆β) = k/(Rα − ∆α) => ∆β = (k/(Rα − ∆α) - Rβ)/γ
        inputAm = (k/(outputReserve - outputA.amount) - inputReserve)/gamma
        return (TokenAmount(inputToken.token, inputAm), [TokenAmount(inputToken.token, inputReserve + inputAm), TokenAmount(outputA.token, outputReserve - outputA.amount)])                
                

    def getLiquidityMinted(self, totalSupply: TokenAmount, tokenAmountA: TokenAmount, tokenAmountB: TokenAmount) -> TokenAmount:
        liquidity = 0
        amount0 = (tokenAmountA.amount*totalSupply.amount)/self.token0.amount
        amount1 = (tokenAmountB.amount*totalSupply.amount)/self.token1.amount
        if amount0 <= amount1:
            liquidity = amount0
        else:
            liquidity = amount1
        return TokenAmount(totalSupply.token, liquidity)
            
    def getLiquidityValue(token: Token, totalSupply: TokenAmount, liquidity: TokenAmount, feeOn: bool = False) -> TokenAmount:
        return TokenAmount(token, (liquidity.amount * token.amount) / totalSupply.amount)

    def __str__(self):
        s = []
        s += ["Pair:"]
        s += [f"  balances:"]
        s += [f"    {self.token0.token.symbol}: {self.token0.amount}"]
        s += [f"    {self.token1.token.symbol}: {self.token1.amount}"]
        s += [f"    {self.liquidityToken.token.symbol}: {self.liquidityToken.amount}"]
        return "\n".join(s)             
              
class Route():
    def __init__(self, symbol: str, name: str):
        self.symbol = symbol
        self.name = name
                          
# event & utility classes
        
class LiquidityPosition():
    def __init__(self, lid: str, pair: Pair, liquidityTokenBalance: int):
        self.uid = lid
        self.pair = pair
        self.liquidityTokenBalance = liquidityTokenBalance

class User():
    def __init__(self, uid: str, liquidityPositions: List[LiquidityPosition], usdSwapped: int):
        self.uid = uid
        self.liquidityPositions = liquidityPositions
        self.usdSwapped = usdSwapped

class Mint():
    def __init__(self, timestamp: int, pair: Pair, to: User, liquidity: float,
                sender: User, amount0: float, amount1: float, feeTo: User, feeLiquidity: float):
        self.timestamp = timestamp
        self.pair = pair
        self.to = to
        self.liquidity = liquidity
        self.sender = sender
        self.amount0 = amount0
        self.amount1 = amount1
        self.feeTo = feeTo
        self.feeLiquidity = feeLiquidity
        
class Burn():
    def __init__(self, timestamp: int, pair: Pair, to: User, liquidity: float,
                sender: User, amount0: float, amount1: float, feeTo: User, feeLiquidity: float):
        self.timestamp = timestamp
        self.pair = pair
        self.to = to
        self.liquidity = liquidity
        self.sender = sender
        self.amount0 = amount0
        self.amount1 = amount1
        self.feeTo = feeTo
        self.feeLiquidity = feeLiquidity

class Swap():
    def __init__(self, timestamp: int, pair: Pair,
                sender: User, amount0In: float, amount1In: float, amount0Out: float, amount1Out: float, to: User):
        self.timestamp = timestamp
        self.pair = pair
        self.sender = sender
        self.amount0In = amount0In
        self.amount1In = amount1In
        self.amount0Out = amount0Out
        self.amount1Out = amount1Out      
        self.to = to
        
class Transaction():
    def __init__(self, transaction_id: str, timestamp: int, mints: List[Mint], burns: List[Burn], swaps: List[Swap]):
        self.transaction_id = transaction_id
        self.timestamp = timestamp
        self.mints = mints
        self.burns = burns
        self.swaps = swaps
        
        
@enforce_types
class UniswapPool():
    def __init__(self, name: str, pair: Pair, swap_fee=SWAP_FEE):
        self.name = name
        self._wallet = AgentWallet(0.0, 0.0)
        self.pair = pair
        self.swap_fee = swap_fee

    def __str__(self):
        s = []
        s += ["UniswapPool:"]
        s += [f"  name = {self.name}"]
        s += [f"  swapFee = %.2f%%" % (self.swap_fee * 100.0)]
        cur_symbols = [self.pair.token0.token.symbol, self.pair.token1.token.symbol]
        s += [f"  currentTokens (as symbols) = {', '.join(cur_symbols)}"] 
        s += [f"  {self.pair}"]
        return "\n".join(s)

        
