"""
Model initial state.
"""

# Dependencies

import random
import uuid
import logging
log = logging.getLogger('simstate')

from enforce_typing import enforce_types # type: ignore[import]
from typing import Set

from parts.agents.BaseAgent import BaseAgent
from parts.agents.AgentDict import AgentDict

from parts.agents.BurnerAgent import BurnerAgent
from parts.agents.TradeAgent import TradeAgent

from parts.agents.LiquidityProviderAgent import LiquidityProviderAgent
from parts.agents.PoolAgent import PoolAgent

from SimStrategy import SimStrategy
from SimState import SimState, funcOne
from parts.agents.util import mathutil, valuation
from parts.agents.util.mathutil import Range
from parts.agents.util.constants import *

from parts.agents.web3engine import uniswappool

import numpy as np
import names
from typing import Tuple, List, Dict
from itertools import cycle
from enum import Enum
import uuid

MAX_DAYS = 3660
OUTPUT_DIR = 'output_test'

## yet to be implemented
agent_probabilities = [0.7,0.75,0.8,0.85,0.9,0.95]

ss = SimStrategy()
ss.setMaxTicks(MAX_DAYS * S_PER_DAY / ss.time_step + 1)
    
assert hasattr(ss, 'save_interval')
ss.save_interval = S_PER_DAY
simState = SimState(ss)

# init agents
# initial_agents = AgentDict()
initial_agents = {}

# set op the Uniswap pools
tokenA = Token(uuid.uuid4(), 'USDC', 'USDC token')
tokenB = Token(uuid.uuid4(), 'ETH', 'Ethereum token')
white_pool_pair = Pair(TokenAmount(tokenA, 200000), TokenAmount(tokenB, 100))
grey_pool_pair = Pair(TokenAmount(tokenA, 3000000), TokenAmount(tokenB, 1500))

white_pool = UniswapPool('White pool', white_pool_pair)
grey_pool = UniswapPool('Grey pool', grey_pool_pair)

#Instantiate and connnect agent instances. "Wire up the circuit"
new_agents = list()

new_agents.append(PoolAgent(
    name = "White Pool", pool = white_pool))

new_agents.append(PoolAgent(
    name = "Grey Pool", pool = grey_pool))

new_agents.append(TradeAgent(
    name = "Trader", USD=0.0, OCEAN=0.0))

new_agents.append(LiquidityProviderAgent(
    name = "Liquidity Provider", USD=0.0, OCEAN=0.0))

new_agents.append(BurnerAgent(
    name = "Burner", USD=0.0, OCEAN=0.0))


for agent in new_agents:
    initial_agents[agent.name] = agent
    print(agent)

from collections import defaultdict

# initial_states = {
#     'granttakers_revenue': 0.0,
#     'revenue_per_marketplace': defaultdict(lambda: 0.0), 
#     'total_OCEAN_staked': defaultdict(lambda: 0.0), 
#     'n_marketplaces': 1,
#     'marketplace_percent_toll_to_ocean': 0.0,
#     'total_OCEAN_minted': 0.0,
#     'total_OCEAN_burned': 0.0,
#     'total_OCEAN_minted_USD': 0.0,
#     'total_OCEAN_burned_USD': 0.0,
# }

genesis_states = {
    'agents': initial_agents,
    'pool_agents': [],
    'state': simState,
    'total_staked': defaultdict(lambda: 0.0), 
}
