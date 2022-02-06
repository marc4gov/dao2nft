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
    roles = params['roles']
    stakeholders = s['stakeholders']
    round = s['round']

    # new Grants round each month
    if (current_timestep % timestep_per_month) == 0:
      round += 1
      # generate new projects
      project_weights, total_stakeholders, total_votes = generate_project_weights(round)
      
      # recurring means how many projects will continue for the next round
      recurring = random.choice(params['recurring_factor'])
      # print("Recurring: ", recurring)
      recurring_factor = math.floor(recurring * len(project_weights))
      recurring_project_names = random.sample(projects.keys(), recurring_factor)
      recurring_projects_total_weight = 0
      recurring_projects = {}
      for name in recurring_project_names:
        recurring_projects[name] = projects[name]
        recurring_projects_total_weight += projects[name].weight
      # new entrant selection
      new_factor = math.floor((1-recurring) * len(project_weights))
      new_entrants = random.sample(project_weights, new_factor)
      new_entrants_total_weight = sum(new_entrants.values())
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
        dao_graph.add_edge('Round ' + str(round), name, weight=weight + missing_weight_per_project)
      # adjust weights per project in recurring projects
      for project_name, team in recurring_projects.items():
        dao_graph.nodes[project_name]['weight'] += missing_weight_per_project
        dao_graph.add_edge('Round ' + str(round), project_name, weight=dao_graph.nodes[project_name]['weight'])

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
      # check milestones progress
      for milestone in project.milestones:
        if abs(current_timestep - milestone.planned) <= 2:
          # do a bend coin flip to determine if a milestone is reached
          reached = random.choice([True, False, False, False])
          if reached:
            milestone.actual = current_timestep
            milestone.delivered = True
        milestones.append(milestone)
      projects[project_name].milestones = milestones
          
      for member, weights in project.team_members.items():
        # do an action per team member (in 80% of the time) or nothing (in 20% of the time)
        new_weight = random.choice([do_discord_action(), do_github_action(), do_contribution_action(), 0])
        if new_weight > 0:
          team[name].append(Weight(new_weight, current_timestep))
          dao_graph.nodes[name]['weight'] = reduce_weigths(team[name], current_timestep)
      projects[project_name] = team

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

    # new Grants round
    # start with 80% of last round's votes
    if (current_timestep % timestep_per_month) == 0:
      return ({
          'valuable_projects': 0,
          'unsound_projects': 0,
          'yes_votes': yes_votes,
          'no_votes': no_votes,
          'nft': nft
      })

    # every day we assess the projects on NFT status and adjust the project properties and vote signal accordingly
    projects = s['projects']
    nft_earners = 0
    for name, team in projects.items():
        if name in nft.keys():
          nft_old = nft[name]
        else:
          nft_old = OceanNFT.SHRIMP
        team_weight = get_team_weight(team, current_timestep)
        nft[name] = mint_nft(team_weight)
        if nft[name].value > nft_old.value:
          nft_earners += 1
    
    # if many projects score NFTs, yes votes will go up
    total_projects = len(projects) if len(projects) > 0 else 1
    nft_earn_ratio = nft_earners/total_projects
    if (nft_earn_ratio > 0.2):
      yes_votes = (1 + (nft_earn_ratio * nft_earn_ratio)) * yes_votes
      no_votes = (1 - (nft_earn_ratio * nft_earn_ratio)) * no_votes
    else:
      yes_votes = (1 - (nft_earn_ratio * nft_earn_ratio)) * yes_votes
      no_votes = (1 + (nft_earn_ratio * nft_earn_ratio)) * no_votes

    # ugly hack - need to change
    valuable = math.floor(random.choice(params['dataset_ratio']) * len(projects))
    valuable_increment = 1
    if valuable <= s['valuable_projects'] and s['valuable_projects'] > 0:
      valuable_increment = -1
    unsound_increment = 1
    unsound = math.floor(random.choice(params['unsound_ratio']) * len(projects))
    if unsound <= s['unsound_projects'] and s['unsound_projects'] > 0:
      unsound_increment = -1  
    
    return ({
        'valuable_projects': s['valuable_projects'] + valuable_increment,
        'unsound_projects': s['unsound_projects'] + unsound_increment,
        'yes_votes': yes_votes,
        'no_votes': no_votes,
        'nft': nft
    })


def curation_policy(params, step, sH, s):
    """
    Update the curation state.
    """
    current_timestep = len(sH)
    timestep_per_day = 1
    timestep_per_week = 7
    timestep_per_month = 30

    curator:Curator = s['curator']
    projects:List[Project] = s['projects']

    # per week or per new Grants round
    if (current_timestep % timestep_per_week) == 0 or (current_timestep % timestep_per_month) == 0:
      for project in projects:
        (delayed, delivered, in_progress, finished) = curateProject(project)
        if not finished:
          if delayed >= 0 and delayed < 3:
            curator.addAudit(project.name, Verdict.DELAYED)
          if delayed >= 3 and delayed < 7:
            curator.addAudit(project.name, Verdict.MILESTONES_NOT_MET)
          if delayed >= 7 and delayed < 14:
            curator.addAudit(project.name, Verdict.FAILED)
          if delayed >= 14 and delayed < 21:
            curator.addAudit(project.name, Verdict.ADVERSARY)
          else:
            curator.addAudit(project.name, Verdict.RUGPULL)
        else:
          curator.addAudit(project.name, Verdict.DELIVERED)

      return({'curator': curator})

    for project in projects:
      (delayed, delivered, in_progress, finished) = curateProject(project)
      if finished:
        curator.addAudit(project.name, Verdict.DELIVERED)
    
    return({'curator': curator})


def participation_policy(params, step, sH, s):
    """
    Update the participation state.
    """
    current_timestep = len(sH)
    timestep_per_day = 1
    timestep_per_month = 30

    # new Grants round
    if (current_timestep % timestep_per_month) == 0:
      if s['voters'] >= s['dao_members']:
        return ({
          'voters': s['voters'],
          'dao_members': s['voters']
        })
      else:
        return ({
          'voters': s['voters'],
          'dao_members': math.floor(s['dao_members'] - 0.1 * s['voters'])
        })

    projects = len(s['projects'])
    unsound_projects = s['unsound_projects'] if s['unsound_projects'] > 0 else 1
    valuable_projects = s['valuable_projects'] if s['valuable_projects'] > 0 else 1
    projects = projects if projects > 0 else 1
    value_ratio = (valuable_projects - unsound_projects) / projects
    voters = math.floor((1 + value_ratio) * s['voters'])
    return ({
      'voters': voters,
      'dao_members': s['dao_members']
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