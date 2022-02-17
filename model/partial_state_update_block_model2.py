"""
Partial state update block. 

Here the partial state update blocks are configurated by setting
- policies
- variables

for each state update block individually
"""
from model.parts.polimechs.values_policy import *
from model.parts.polimechs.accounting_policy import *
from model.parts.polimechs.projects_policy import *
from model.parts.polimechs.update_state import *

partial_state_update_block = [
    {
        'policies': {
            'values_policy': values_policy,
        },
        'variables': {
            'yes_votes': update_yes_votes,
            'no_votes': update_no_votes,
            'weight_rate': update_weight_rate,
            'nft': update_nft,
        },
    },
    {
        'policies': {
            'accounting_policy': accounting_policy,
        },
        'variables': {
            'voters': update_voters,
            'dao_members': update_dao_members
        }
    },
    {
        'policies': {
            'projects_policy': projects_policy,
        },
        'variables': {
            'projects': update_projects,
            'round': update_round,
            'dao_graph': update_dao_graph
        }
    },

]