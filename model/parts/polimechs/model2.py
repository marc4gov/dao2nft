import math
import random
from model.parts.agents.Curator import Curator, Verdict
from model.parts.agents.Project import Project
import names

import networkx as nx
from model.parts.agents.util.sourcecred.contribution import *
from model.parts.agents.util.sourcecred.contributor import *
from typing import List, Dict

def grants_policy(params, step, sH, s):
    """
    Update the grants state.
    """
    current_timestep = len(sH)
    timestep_per_day = 1
    timestep_per_month = 30

    # adjust the grant CAP according to the amount of valuable projects in this round
    if (current_timestep % timestep_per_month) == 0:
      total_projects = len(s['projects']) if len(s['projects']) > 0 else 1
      value_ratio = (s['valuable_projects'] - s['unsound_projects']) / total_projects
      return ({'grant_cap': math.floor((1 + value_ratio) * s['grant_cap'])})

    return ({'grant_cap': s['grant_cap'] })

def projects_policy(params, step, sH, s):
    """
    Update the projects state.
    """
    current_timestep = len(sH)
    timestep_per_day = 1
    timestep_per_week = 7
    timestep_per_month = 30

    dao_graph:nx.DiGraph = s['dao_graph']
    projects:Dict[str, Project] = s['projects']
    round = s['round']

    # new Grants round each month
    if (current_timestep % timestep_per_month) == 0:
      round += 1
      # generate new projects
      project_weights, total_stakeholders, total_votes = generate_project_weights(round)
      
      # recurring means how many projects will continue for the next round
      recurring = random.choice(params['recurring_factor'])
      print("Recurring: ", recurring)
      recurring_factor = math.floor(recurring * len(projects))
      recurring_project_names = random.sample(list(projects), recurring_factor)
      recurring_projects_total_weight = 0
      recurring_projects = {}
      for name in recurring_project_names:
        recurring_projects[name] = projects[name]
        recurring_projects_total_weight += projects[name].weight
        # print(recurring_projects[name])

      # new entrant selection
      new_factor = math.floor((1-recurring) * len(project_weights))
      new_entrants_names = random.sample(list(project_weights), new_factor)
      new_entrants_total_weight = 0
      new_entrants = {}
      for name in new_entrants_names:
        new_entrants[name] = project_weights[name]
        new_entrants_total_weight += project_weights[name]
      # weights are offset because of random selections
      missing_weight = 1 - (recurring_projects_total_weight + new_entrants_total_weight)
      total_new_entrants = len(new_entrants) if len(new_entrants) > 0 else 1
      total_recurring_projects = len(recurring_projects) if len(recurring_projects) > 0 else 1
      missing_weight_per_project = missing_weight/(total_new_entrants + total_recurring_projects)
      # init the new entrants
      for name, weight in new_entrants.items():
        new_weight = weight + missing_weight_per_project
        team = generate_project(name, new_weight, current_timestep, math.floor(total_votes * weight))
        new_entrants[name] = team
        dao_graph.add_node(name)
        dao_graph.add_edge('Round ' + str(round), name)
      # adjust weights and milestones per project in recurring projects
      for name, project in recurring_projects.items():
        project.weight += missing_weight_per_project
        project.reset()
        project.generateMilestones(current_timestep)
        recurring_projects[name] = project
        
      # merge the new entrants and the recurring projects
      projects = {**recurring_projects, **new_entrants}

      return ({
          'projects': projects,
          'dao_graph': dao_graph,
          'round': round
      })

    # actions in projects by week
    if (current_timestep % timestep_per_week) == 0:
      for project in projects.values():
        # check milestones progress
        pass

    # actions in projects by day
    for project_name, project in projects.items():
      milestones = []
      # check milestones & tasks in progress
      projects[project_name].milestones = check_milestones(projects[project_name].milestones, current_timestep)
      members = []
      for member in project.team_members:
        # do an action per team member (in 75% of the time) or nothing (in 25% of the time)
        new_weight = random.choice([do_discord_action(), do_github_action(), do_contribution_action(), 0])
        if new_weight > 0:
          member.weights.append(Weight(new_weight, current_timestep))
        members.append(member)
      project.team_members = members
      projects[project_name] = project

    return ({
      'projects': projects,
      'dao_graph': dao_graph,
      'round': round
    })


def values_policy(params, step, sH, s):
    """
    What kind of projects and team members deliver value?
    """
    current_timestep = len(sH)
    timestep_per_day = 1
    timestep_per_month = 30
    nft = s['nft']
    yes_votes = s['yes_votes']
    no_votes = s['no_votes']
    weight_rate = s['weight_rate']

    # new Grants round
    if (current_timestep % timestep_per_month) == 0:
      projects = s['projects']
      nft_earners = 0
      # if many projects score NFTs, yes votes will go up
      total_projects = len(projects) if len(projects) > 0 else 1
      nft_earn_ratio = nft_earners/total_projects
      if (nft_earn_ratio > 0.2):
        yes_votes = (1 + (nft_earn_ratio * nft_earn_ratio)) * yes_votes
        no_votes = (1 - (nft_earn_ratio * nft_earn_ratio)) * no_votes
      else:
        yes_votes = (1 - (nft_earn_ratio * nft_earn_ratio)) * yes_votes
        no_votes = (1 + (nft_earn_ratio * nft_earn_ratio)) * no_votes
      return ({
          'weight_rate': {},
          'yes_votes': yes_votes,
          'no_votes': no_votes,
          'nft': nft
      })

    # every day we assess the projects on NFT status and adjust the project properties and vote signal accordingly
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



# state update functions

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