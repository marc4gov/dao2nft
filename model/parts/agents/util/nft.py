import math

class Weight:
    def __init__(self, total: float, timestep: int):
        self.total: float = total
        self.genesis_timestep: int = timestep

    def decay(self, current_timestep):
      half_life = [0.8**i for i in range(50)]
      time_passed = current_timestep - self.genesis_timestep
      if time_passed % 7 == 0:
        self.total *= half_life[math.floor(time_passed/7)]
