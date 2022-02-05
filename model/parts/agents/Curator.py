from .util.nft import Weight
from .util.wallet import Wallet
from typing import List, Tuple
import uuid
from enum import Enum

class Verdict(Enum):
    DELIVERED = 0
    DELAYED = 1
    MILESTONES_NOT_MET = 2
    FAILED = 3
    ADVERSARY = 4
    RUGPULL = 5

class Curator(Weight):
    def __init__(self, name: str, weight: float, timestep: int, wallet: Wallet):
        super().__init__(weight, timestep)
        self.name = name
        self.uuid = uuid.uuid4()
        self.wallet = wallet
        self.audits:List[Tuple] = []

    def addAudit(self, project_name, verdict:Verdict):
        self.audits.append((project_name, verdict))

    def winTokens(self, amount):
        self.wallet.depositOCEAN(amount)
    
    def slashTokens(self, amount):
        self.wallet.withdrawOCEAN(amount)

    def __str__(self) -> str:
        s = []
        s += ["\nCurator={\n"]
        s += ['name=%s' % self.name]
        s += ['; weight=%s' % self.weight]
        s += ['; wallet=%s' % self.wallet]
        s += ['; audits=%s' % ",".join(map(str, self.audits))]
        s += [" \n/Curator}"]
        return "".join(s)
