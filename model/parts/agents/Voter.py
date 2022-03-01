from .util.nft import Weight
from .util.wallet import Wallet
from typing import List, Tuple
import uuid

class Voter(Weight):
    def __init__(self, name: str, weight: float, timestep: int, wallet: Wallet):
        super().__init__(weight, timestep)
        self.name = name
        self.uuid = uuid.uuid4()
        self.wallet = wallet
        self.votes:List[Tuple] = []
        self.won:float = 0.0
        self.lost:float = 0.0

    def addVote(self, project_name, amount):
        self.votes.append((project_name, amount))

    def winTokens(self, amount):
        self.wallet.depositOCEAN(amount)
        self.won += amount
    
    def slashTokens(self, amount):
        self.wallet.withdrawOCEAN(amount)
        self.lost += amount

    def __str__(self) -> str:
        s = []
        s += ["\nVoter={\n"]
        s += ['name=%s' % self.name]
        s += ['; weight=%s' % self.current_weight]
        s += ['; wallet=%s' % self.wallet]
        s += ['; votes=%s' % ",".join(map(str, self.votes))]
        s += ["\n/Voter}"]
        return "".join(s)
