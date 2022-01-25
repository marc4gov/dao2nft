"""
Partial state update block. 

Here the partial state update blocks are configurated by setting
- policies
- variables

for each state update block individually
"""
from .parts.polimechs.model2 import *

partial_state_update_block = [
    {
        'policies': {
            'grants_policy': grants_policy,
            'values_policy': values_policy,
            'participation_policy': participation_policy
        },
        'variables': {
            'grant_cap': update_grants,
            'valuable_projects': update_valuable_projects,
            'unsound_projects': update_unsound_projects,
            'yes_votes': update_yes_votes,
            'no_votes': update_no_votes,
            'voters': update_voters,
            'dao_members': update_dao_members
        },
    },
    {
        'policies': {
            'projects_policy': projects_policy,
        },
        'variables': {
            'projects': update_projects,
            'dao_graph': update_dao_graph,
            'round': update_round
        }
    }
]