"""
Model initial state.
"""

import networkx as nx
import math
from model.parts.agents.util.sourcecred.contributor import probabilities, generate_voters, generate_project, generate_project_weights
from .sys_params_model2 import params
from model.parts.agents.Curator import Curator
from model.parts.agents.util.wallet import Wallet

dao_graph = nx.DiGraph()
dao_graph.add_node('Round 1')

# weights = probabilities(126, 1.0, 0.6, 4_012_000)
projects = {}

project_weights, total_stakeholders, total_votes = generate_project_weights(13)
voters = generate_voters(1, 0, project_weights)
for name, weight in project_weights.items():
    project = generate_project(name, weight, 0, math.floor(200_000 * weight))
    projects[name] = project
    dao_graph.add_node(name)
    dao_graph.add_edge('Round 1', name, weight=weight)

genesis_state = {
    'dao_members': 100,
    'voters': voters,
    'grant_cap': 200_000,
    'projects': projects,
    'yes_votes': 30,
    'no_votes': 10,
    'valuable_projects': 0,
    'unsound_projects': 0,
    'dao_graph': dao_graph,
    'nft': {},
    'weight_rate': {},
    'round': 1
}