"""
Model initial state.
"""

import networkx as nx

projects = [nx.DiGraph()]
dao_graph = nx.DiGraph()

genesis_state = {
    'dao_members': 100,
    'voters': 50,
    'grant_cap': 200,
    'projects': projects,
    'yes_votes': 30,
    'no_votes': 10,
    'valuable_projects': 0,
    'unsound_projects': 0,
    'agents' : [],
    'dao_graph': dao_graph
}
