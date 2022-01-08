import logging
log = logging.getLogger('baseagent')

from abc import ABC, abstractmethod
from enforce_typing import enforce_types # type: ignore[import]
import typing

from . import AgentWallet
# from web3engine import unipool, datatoken, globaltokens
from .util.constants import SAFETY
from .util.strutil import StrMixin
from .web3tools.web3util import toBase18

@enforce_types
class BaseAgent(ABC, StrMixin):
    """This can be a liquidity provider, arbitrageur, etc. Sub-classes implement each."""
       
    def __init__(self, name: str, USD: float, ETH: float):
        self.name = name
        self._wallet = AgentWallet.AgentWallet(USD, ETH)

        #postconditions
        assert self.USD() == USD
        assert self.ETH() == ETH

    #=======================================================================
    @abstractmethod
    def takeStep(self, state): #this is where the Agent does *work*
        pass

    #=======================================================================
    #USD-related
    def USD(self) -> float:
        return self._wallet.USD() 
    
    def receiveUSD(self, amount: float) -> None:
        self._wallet.depositUSD(amount) 

    def payUSD(self, amount: float) -> None:
        self._wallet.withdrawUSD(amount)
        
    #=======================================================================
    #ETH-related
    def ETH(self) -> float:
        return self._wallet.ETH() 
    
    def receiveETH(self, amount: float) -> None:
        self._wallet.depositETH(amount) 

    def payETH(self, amount: float) -> None:
        self._wallet.withdrawETH(amount)
                            
