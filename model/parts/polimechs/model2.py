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
    round = s['round']

    # new Grants round each month
    if (current_timestep % timestep_per_month) == 0:
      round += 1
      # generate new projects
      project_weights, total_stakeholders, total_votes = generate_project_weights(round)
      
      # recurring means how many projects will continue for the next round
      recurring = random.choice(params['recurring_factor'])
      # print("Recurring: ", recurring)
      recurring_factor = math.floor(recurring * len(projects))
      recurring_project_names = random.sample(list(projects), recurring_factor)
      recurring_projects_total_weight = 0
      recurring_projects = {}
      for name in recurring_project_names:
        recurring_projects[name] = projects[name]
        recurring_projects_total_weight += projects[name].weight
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
      # adjust weights per project in recurring projects
      for project_name, team in recurring_projects.items():
        dao_graph.add_edge('Round ' + str(round), project_name)

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
          reached = random.choice([True, True, True, False])
          if reached:
            milestone.actual = current_timestep
            milestone.delivered = True
        milestones.append(milestone)
      projects[project_name].milestones = milestones
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
    for project_name, project in projects.items():
        if project_name in nft.keys():
          nft_old = nft[project_name]
        else:
          nft_old = OceanNFT.SHRIMP
        team_weight = get_team_weight(project.team_members, current_timestep)
        nft[project_name] = mint_nft(team_weight)
        if nft[project_name].value > nft_old.value:
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
    projects = s['projects']

    # per week or per new Grants round
    if (current_timestep % timestep_per_week) == 0 or (current_timestep % timestep_per_month) == 0:
      for project in projects.values():
        (delayed, delivered, in_progress, finished) = curateProject(project, current_timestep)
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

    for project_name, project in projects.items():
      (delayed, delivered, in_progress, finished) = curateProject(project, current_timestep)
      if finished:
        curator.addAudit(project_name, Verdict.DELIVERED)
    
    return({'curator': curator})


def participation_policy(params, step, sH, s):
    """
    Update the participation state.
    """
    current_timestep = len(sH)
    timestep_per_day = 1
    timestep_per_month = 30

    voters = s['voters']
    total_votes = get_total_votes(voters)
    curator = s['curator']
    # new Grants round
    if (current_timestep % timestep_per_month) == 0:
      #do accounting
      voters = accounting(curator, voters)
      total_votes_accounted = get_total_votes(voters)
      ratio = total_votes_accounted/total_votes
      if total_votes_accounted >= total_votes:
        return ({
          'voters': voters,
          'dao_members': math.floor(s['dao_members'] + ratio * len(voters))
        })
      else:
        return ({
          'voters': voters,
          'dao_members': math.floor(s['dao_members'] - ratio * len(voters))
        })

    # projects = len(s['projects'])
    # unsound_projects = s['unsound_projects'] if s['unsound_projects'] > 0 else 1
    # valuable_projects = s['valuable_projects'] if s['valuable_projects'] > 0 else 1
    # projects = projects if projects > 0 else 1
    # value_ratio = (valuable_projects - unsound_projects) / projects
    # voters = math.floor((1 + value_ratio) * s['voters'])
    return ({
      'voters': s['voters'],
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

def update_curator(params, step, sH, s, _input):
  return ('curator', _input['curator'])