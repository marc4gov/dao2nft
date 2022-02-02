"""
Model initial state.
"""

import networkx as nx
from model.parts.agents.util.sourcecred.contributor import probabilities, generate_stakeholders, generate_projects, generate_project_graph
from .sys_params_model2 import params

dao_graph = nx.DiGraph()
dao_graph.add_node('Round 1')

weights = probabilities(126, 1.0, 0.6, 4_012_000)
projects = {}

stakeholders = generate_stakeholders(weights)
projects_weights, total_stakeholders, total_votes = generate_projects(13)
for name, weight in projects_weights.items():
    team, project_graph = generate_project_graph(name, weight, params['roles'][0].copy(), 0)
    projects[name] = team
    dao_graph.add_node(name)
    attrs = {name: {"Milestone1": False, "Milestone2": False, "Milestone3": False, "Milestone4": False, "Finished": False, "ROI": False}}
    nx.set_node_attributes(dao_graph, attrs)
    dao_graph.add_edge('Round 1', name, weight=weight)
    dao_graph = nx.compose(dao_graph, project_graph)

genesis_state = {
    'dao_members': 100,
    'voters': 50,
    'grant_cap': 200,
    'projects': projects,
    'yes_votes': 30,
    'no_votes': 10,
    'valuable_projects': 0,
    'unsound_projects': 0,
    'stakeholders': stakeholders,
    'dao_graph': dao_graph,
    'nft': {},
    'round': 1
}