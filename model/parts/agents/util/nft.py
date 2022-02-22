import math
from .sourcecred.contribution import OceanNFT

import numpy as np

def reverse_sigmoid(x):
    z = np.exp(x)
    sig = 2 / (1 + z)
    return sig

class Weight:
    def __init__(self, weight: float, timestep: int):
        self.initial_weight: float = weight
        self.genesis_timestep: int = timestep
        self.current_weight = 0

    def decay(self, current_timestep):
        time_passed = current_timestep - self.genesis_timestep
        self.current_weight = reverse_sigmoid(0.1 * time_passed) * self.initial_weight

class NFT:
    def __init__(self, nft_type: OceanNFT):
        self.type = nft_type