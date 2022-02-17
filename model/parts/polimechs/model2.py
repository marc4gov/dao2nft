import math

from model.parts.agents.util.sourcecred.contributor import get_team_weight, mint_nft, OceanNFT
from typing import List, Dict


def values_policy(params, step, sH, s):
    """
    What kind of projects and team members deliver value?
    """
    current_timestep = len(sH)
    timestep_per_day = 1
    timestep_per_week = 7
    timestep_per_midweek = 3
    timestep_per_month = 30
    nft = s['nft']
    yes_votes = s['yes_votes']
    no_votes = s['no_votes']
    weight_rate = s['weight_rate']
    projects = s['projects']

    # new Grants round
    if (current_timestep % timestep_per_week) == 0:
      nft_sorted = sorted(nft.values(), key=lambda x: x[1], reverse=True)
      total = len(nft_sorted) if len(nft_sorted) > 0 else 1
      nft_values = [v[1] for v in nft_sorted]
      avg = sum(nft_values)/total
      nft_performer = 0
      # if many projects have weights above avg, yes votes will go up
      for weight in nft_values:
        if weight > avg:
          nft_performer += 1
      nft_earn_ratio = nft_performer/total
      # the performance level is driver for yes or no votes, assuming linear to the square of the ratio
      if (nft_earn_ratio > params['performer_ratio']):
        yes_votes = (1 + (nft_earn_ratio ** 2)) * yes_votes
        no_votes = (1 - (nft_earn_ratio ** 2)) * no_votes
      else:
        yes_votes = (1 - (nft_earn_ratio ** 2)) * yes_votes
        no_votes = (1 + (nft_earn_ratio ** 2)) * no_votes
      return ({
          'weight_rate': weight_rate,
          'yes_votes': yes_votes,
          'no_votes': no_votes,
          'nft': nft
      })

    # every day we assess the projects on accumulated weights and adjust the project properties accordingly
    for project_name, project in projects.items():
        if project_name in nft.keys():
          nft_old = nft[project_name][0]
          old_weight = nft[project_name][1]
        else:
          nft_old = OceanNFT.SHRIMP
          old_weight = 0
        team_weight = get_team_weight(project.team_members, current_timestep)
        weight_rate[project_name] = team_weight - old_weight
        nft[project_name] = (mint_nft(team_weight), team_weight)
    
    return ({
        'weight_rate': weight_rate,
        'yes_votes': yes_votes,
        'no_votes': no_votes,
        'nft': nft
    })


# boilerplate state update functions

def update_grants(params, step, sH, s, _input):
  return ('grant_cap', _input['grant_cap'])

def update_projects(params, step, sH, s, _input):
  return ('projects', _input['projects'])

def update_agents(params, step, sH, s, _input):
  return ('agents', _input['agents'])

def update_dao_graph(params, step, sH, s, _input):
  return ('dao_graph', _input['dao_graph'])

def update_valuable_projects(params, step, sH, s, _input):
  return ('valuable_projects', _input['valuable_projects'])

def update_unsound_projects(params, step, sH, s, _input):
  return ('unsound_projects', _input['unsound_projects'])

def update_weight_rate(params, step, sH, s, _input):
  return ('weight_rate', _input['weight_rate'])

def update_yes_votes(params, step, sH, s, _input):
  return ('yes_votes', _input['yes_votes'])

def update_no_votes(params, step, sH, s, _input):
  return ('no_votes', _input['no_votes'])

def update_voters(params, step, sH, s, _input):
  return ('voters', _input['voters'])

def update_dao_members(params, step, sH, s, _input):
  return ('dao_members', _input['dao_members'])

def update_round(params, step, sH, s, _input):
  return ('round', _input['round'])

def update_nft(params, step, sH, s, _input):
  return ('nft', _input['nft'])

def update_curator(params, step, sH, s, _input):
  return ('curator', _input['curator'])