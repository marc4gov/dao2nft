from enforce_typing import enforce_types # type: ignore[import]
import typing
import requests
import uuid

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
        
class Pair():
    def __init__(self, token0: TokenAmount, token1: TokenAmount):
        self.token0 = token0
        self.token1 = token1
        liquidity = Math.sqrt(token0.amount*token1.amount)
        self.liquidityToken = TokenAmount(Token(uuid.uuid4(), 'UNI-V2', 'Uniswap V2'), liquidity)
        self.txCount = 1
        
    def token0Price() -> float:
        return self.token1.token.amount/self.token0.token.amount
    
    def token1Price() -> float:
        return self.token0.token.amount/self.token1.token.amount
    
    def reserve0() -> TokenAmount:
        return self.token0
    
    def reserve1() -> TokenAmount:
        return self.token1
    
    def reserveOf(token: Token) -> TokenAmount:
        if token == self.token0.token:
            return self.reserve0
        else:
            return self.reserve1
    
    def getOutputAmount(inputAmount: TokenAmount) -> (TokenAmount, [TokenAmount]):
        inputReserve = self.reserveOf(inputAmount.token).amount
        outputtoken = self.token1.token
        if inputAmount.token == self.token1.token:
            outputtoken = self.token0.token
        outputReserve = self.reserveOf(outputtoken).amount
        k = inputReserve * outputReserve
        gamma = 1 - SWAP_FEE
        # Transactions must satisfy (Rα − ∆α)(Rβ + γ∆β) = k
        # (Rα − ∆α) = k/(Rβ + γ∆β) => ∆α = Rα - k/(Rβ + γ∆β)
        output = ouputReserve - k/(inputReserve + gamma*inputAmount.amount)
        return (TokenAmount(outputtoken, output), [TokenAmount(inputAmount.token, inputReserve + inputAmount.amount), TokenAmount(outputtoken, outputReserve - output)])

    def getInputAmount(outputAmount: TokenAmount) -> (TokenAmount, [TokenAmount]):
        outputReserve = self.reserveOf(outputAmount.token).amount
        inputtoken = self.token0.token
        if outputAmount.token == self.token0.token:
            inputtoken = self.token1.token
        inputReserve = self.reserveOf(inputtoken).amount
        k = inputReserve * outputReserve
        gamma = 1 - SWAP_FEE
        
        # Transactions must satisfy (Rα − ∆α)(Rβ + γ∆β) = k
        # (Rβ + γ∆β) = k/(Rα − ∆α) => ∆β =  (k/(Rα − ∆α) - Rβ)/γ
        inputAm = (k/(outputReserve - outputAmount.amount) - inputReserve)/gamma
        return ( TokenAmount(inputtoken, inputAm), [TokenAmount(inputtoken, inputReserve + inputAm),  TokenAmount(outputAmount.token, outputReserve - outputAmount.amount)])                
                

    def getLiquidityMinted(totalSupply: TokenAmount, tokenAmountA: TokenAmount, tokenAmountB: TokenAmount) -> TokenAmount:
        liquidity = 0
        if totalSupply.amount == 0:
            liquidity = Math.sqrt(tokenAmountA.amount*tokenAmountB.amount)
        else:
            amount0 = (tokenAmountA.amount*totalSupply.amount)/self.reserve0.amount
            amount1 = (tokenAmounBA.amount*totalSupply.amount)/self.reserve1.amount
            if amount0 <= amount1:
                liquidity = amount0
            else:
                liquidity = amount1
        return  Token(totalSupply.token, liquidity)
            
    def getLiquidityValue(token: Token, totalSupply: TokenAmount, liquidity: TokenAmount, feeOn: bool = False) -> TokenAmount:
        return  TokenAmount(token, (liquidity.amount * token.amount) / totalSupply.amount)
                
              
class Route():
    def __init__(self, route_id: str, symbol: str, name: str):
        self.token_id = token_id
        self.symbol = symbol
        self.name = name
                          
# event & utility classes
        
class LiquidityPosition():
    def __init__(self, lid: str, pair: Pair, liquidityTokenBalance: int):
        self.uid = lid
        self.pair = pair
        self.liquidityTokenBalance = liquidityTokenBalance

class User():
    def __init__(self, uid: str, liquidityPositions: [LiquidityPosition], usdSwapped: int):
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
    def __init__(self, transaction_id: str, timestamp: int, mints: [Mint], burns: [Burn], swaps: [Swap]):
        self.transaction_id = transaction_id
        self.timestamp = timestamp
        self.mints = mints
        self.burns = burns
        self.swaps = swaps
        
        
@enforce_types
class UniswapPool():
    def __init__(self, name: str, pair: Pair):
        self.name = name
        self._wallet = AgentWallet.AgentWallet(0, 0)
        self.pair = pair
        self.swap_fee = 0.003

    def __str__(self):
        s = []
        s += ["UniswapPool:"]
        s += [f"  name={self.name}"]
        s += ["  swapFee = %.2f%%" % (swap_fee * 100.0)]
        cur_symbols = [self.pair.token0.symbol, self.pair.token1.symbol]
        s += [f"  currentTokens (as symbols) = {', '.join(cur_symbols)}"] 
        s += [f"  balances:"]
        s += [f"    {self.pair.token0.symbol}: {self.pair.reserve0}"]
        s += [f"    {self.pair.token1.symbol}: {self.pair.reserve1}"]
        return "\n".join(s)

        
