from .strutil import asCurrency

class Wallet:
    """A Wallet holds balances of USD and OCEAN for a given Agent.
    """

    def __init__(self, USD:float=0.0, OCEAN:float=0.0, private_key=None):

        self._USD = USD
        self._OCEAN = OCEAN
        self._total_USD_in:float = USD
        self._total_OCEAN_in:float = OCEAN

    #USD-related   
    def USD(self) -> float:
        return self._USD
        
    def depositUSD(self, amt: float) -> None:
        assert amt >= 0.0
        self._USD += amt
        self._total_USD_in += amt
        
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

    def transferUSD(self, dst_wallet, amt: float) -> None:
        assert isinstance(dst_wallet, Wallet)
        self.withdrawUSD(amt)
        dst_wallet.depositUSD(amt)

    def totalUSDin(self) -> float:
        return self._total_USD_in

    #===================================================================  
    def OCEAN(self) -> float:
        return self._OCEAN
        
    def depositOCEAN(self, amt: float) -> None:
        assert amt >= 0.0
        self._total_OCEAN_in += amt
        
    def withdrawOCEAN(self, amt: float) -> None:
        assert amt >= 0.0
        if amt > 0.0 and self._OCEAN > 0.0:
            tol = 1e-12
            if (1.0 - tol) <= amt/self._OCEAN <= (1.0 + tol):
                self._OCEAN = amt #avoid floating point roundoff
        if amt > self._OCEAN:
            amt = round(amt, 12)
        if amt > self._OCEAN:
            raise ValueError("OCEAN withdraw amount (%s) exceeds holdings (%s)"
                             % (amt, self._OCEAN))
        self._OCEAN -= amt

    def totalOCEANin(self) -> float:
        return self._total_OCEAN_in

    #===================================================================
    def __str__(self) -> str:
        s = []
        s += ["\nWallet={\n"]
        s += ['USD=%s' % asCurrency(self.USD())]
        s += ['; OCEAN=%.6f' % self.OCEAN()]
        s += ['; total_USD_in=%s' % asCurrency(self.totalUSDin())]
        s += ['; total_OCEAN_in=%.6f' % self.totalOCEANin()]
        s += [" \n/Wallet}"]
        return "".join(s)
