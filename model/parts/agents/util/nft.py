import math
from .sourcecred.contribution import OceanNFT

class Weight:
    def __init__(self, weight: float, timestep: int):
        self.weight: float = weight
        self.genesis_timestep: int = timestep

    def decay(self, current_timestep):
      half_life = [0.8**i for i in range(50)]
      time_passed = current_timestep - self.genesis_timestep
      if time_passed % 7 == 0:
        self.weight *= half_life[math.floor(time_passed/7)]

class NFT:
    def __init__(self, nft_type: OceanNFT):
        self.type = nft_type