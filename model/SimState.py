import logging
log = logging.getLogger('simstate')

from enforce_typing import enforce_types # type: ignore[import]
from typing import Set
import requests

from .SimStrategy import SimStrategy
from .parts.agents.util import mathutil, valuation
from .parts.agents.util.mathutil import Range
from .parts.agents.util.constants import *
from .parts.agents.web3engine.uniswappool import Token

@enforce_types
class SimState(object):

    def __init__(self, ss: SimStrategy):
        log.debug("init:begin")

        #main
        self.ss = ss
        self.tick = 0

        self.tokenA = None
        self.tokenB = None
        self.white_pool_volume_USD: float = 0.0
        self.grey_pool_volume_USD: float = 0.0
        self.white_pool_volume_ETH: float = 0.0
        self.grey_pool_volume_ETH: float = 0.0
        self._total_Liq_minted_White: float = 0.0
        self._total_Liq_minted_Grey: float = 0.0
        self._total_Liq_supply_White: float = 0.0
        self._total_Liq_supply_Grey: float = 0.0
        self._total_Liq_burned_White: float = 0.0
        self._total_Liq_burned_Grey: float = 0.0

        log.debug("init: end")

    def takeStep(self, agents) -> None:
        """This happens once per tick"""
        self.tick += 1


    # def tokenPrice(self, token:Token) -> float:
    #     r0 = requests.get("https://min-api.cryptocompare.com/data/price?fsym=" + token.symbol + "&tsyms=USD")
    #     return r0.json()['USD']

    # #==============================================================
    # def OCEANprice(self) -> float:
    #     """Estimated price of $OCEAN token, in USD"""
    #     price = valuation.OCEANprice(self.overallValuation(),
    #                                  self.OCEANsupply())
    #     assert price > 0.0
    #     return price

    # #==============================================================
    # def overallValuation(self) -> float: #in USD
    #     v = self.fundamentalsValuation() + \
    #         self.speculationValuation()
    #     assert v > 0.0
    #     return v

    # def fundamentalsValuation(self) -> float: #in USD
    #     return self.kpis.valuationPS(30.0) #based on P/S=30                     #magic number

    # def speculationValuation(self) -> float: #in USD
    #     return self._speculation_valuation

    # #==============================================================


def funcOne():
    return 1.0
