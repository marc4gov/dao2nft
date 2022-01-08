import logging
log = logging.getLogger('wallet')

from enforce_typing import enforce_types # type: ignore[import]
import typing

# from web3engine import bpool, datatoken, globaltokens
from .util import constants 
from .util.strutil import asCurrency
# from web3tools import web3util, web3wallet
# from web3tools.web3util import fromBase18, toBase18

@enforce_types
class AgentWallet:
    """An AgentWallet holds balances of USD and other assets for a given Agent.

    """

    def __init__(self, USD:float=0.0, ETH:float=0.0):
        
        #USDC
        self._USD = USD
        self._ETH = ETH
        
    #=================================================================== 
    #USD-related   
    def USD(self) -> float:
        return self._USD
        
    def depositUSD(self, amt: float) -> None:
        assert amt >= 0.0
        self._USD += amt
        
    def withdrawUSD(self, amt: float) -> None:
        assert amt >= 0.0
        if amt > 0.0 and self._USD > 0.0:
            tol = 1e-12
            if (1.0 - tol) <= amt/self._USD <= (1.0 + tol):
                self._USD = amt #avoid floating point roundoff
        if amt > self._USD:
            amt = round(amt, 12)
        if amt > self._USD:
            raise ValueError("USD withdraw amount (%s) exceeds holdings (%s)"
                             % (amt, self._USD))
        self._USD -= amt

    #=================================================================== 
    #ETH-related   
    def ETH(self) -> float:
        return self._ETH
        
    def depositETH(self, amt: float) -> None:
        assert amt >= 0.0
        self._ETH += amt
        
    def withdrawETH(self, amt: float) -> None:
        assert amt >= 0.0
        if amt > 0.0 and self._ETH > 0.0:
            tol = 1e-12
            if (1.0 - tol) <= amt/self._ETH <= (1.0 + tol):
                self._ETH = amt #avoid floating point roundoff
        if amt > self._ETH:
            amt = round(amt, 12)
        if amt > self._ETH:
            raise ValueError("ETH withdraw amount (%s) exceeds holdings (%s)"
                             % (amt, self._ETH))
        self._ETH -= amt

        
    #===================================================================
    def __str__(self) -> str:
        s = []
        s += ["AgentWallet={"]
        s += ['USD=%s' % asCurrency(self.USD())]
        s += ['; ETH=%.6f' % self.ETH()]
        s += [" /AgentWallet}"]
        return "".join(s)

