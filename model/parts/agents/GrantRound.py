from .util.wallet import Wallet
from typing import List
import uuid

class GrantRound():
    def __init__(self, name: str, id: int, wallet: Wallet):
        self.name = name
        self.id = id
        self.wallet = wallet
        self.projects = []

    def addProject(self, project):
        self.projects.append(project)

    def __str__(self) -> str:
        s = []
        s += ["GrantRound={\n"]
        s += ['name=%s' % self.name]
        s += ['; wallet=%s' % self.wallet]
        s += ['; Projects=%s' % self.projects]
        s += [" /GrantRound}"]
        return "".join(s)
