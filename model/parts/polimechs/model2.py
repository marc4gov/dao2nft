import math
import random
import names

import networkx as nx
from model.parts.agents.util.sourcecred.contribution import *
from model.parts.agents.util.sourcecred.contributor import *

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
    projects = s['projects']
    roles = params['roles']
    stakeholders = s['stakeholders']
    round = s['round']

    # new Grants round each month
    if (current_timestep % timestep_per_month) == 0:
      round += 1
      # generate new projects
      project_weights, total_stakeholders, total_votes = generate_projects(round)
      
      # recurring means how many projects will continue for the next round
      recurring = random.choice(params['recurring_factor'])
      # print("Recurring: ", recurring)
      recurring_factor = math.floor(recurring * len(project_weights))
      recurring_projects = select_entities(recurring_factor, projects)
      recurring_projects_total_weight = 0
      for name in recurring_projects.keys():
        recurring_projects_total_weight += dao_graph.nodes[name]['weight']
      # new entrant selection
      new_factor = math.floor((1-recurring) * len(project_weights))
      new_entrants = select_entities(new_factor, project_weights)
      new_entrants_total_weight = sum(new_entrants.values())
      # weights are offset because of random selections
      missing_weight = 1 - (recurring_projects_total_weight + new_entrants_total_weight)
      total_new_entrants = len(new_entrants) if len(new_entrants) > 0 else 1
      total_recurring_projects = len(recurring_projects) if len(recurring_projects) > 0 else 1
      missing_weight_per_project = missing_weight/(total_new_entrants + total_recurring_projects)
      # init the new entrants
      for name, weight in new_entrants.items():
        team, project_graph = generate_project_graph(name, weight + missing_weight_per_project, roles.copy(), current_timestep)
        new_entrants[name] = team
        dao_graph.add_node(name)
        dao_graph.add_edge('Round ' + str(round), name, weight=weight + missing_weight_per_project)
        dao_graph = nx.compose(dao_graph, project_graph)
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
      for project_name, team in projects.items():
        # check milestones progress
        project_attrs = dao_graph.nodes[project_name]
        milestone_nr = check_last_milestone(project_attrs)
        # do a coin flip to determine if a milestone is reached
        flipped = random.choice([True, False])
        if flipped:
          milestone_nr += 1
          cred = reach_milestone(milestone_nr, dao_graph.nodes[project_name]['weight'])
          dao_graph.nodes[project_name]['Milestone' + str(milestone_nr)] = True
          team = append_team_weights(team, cred/len(team), current_timestep)
          for name, weights in team.items():
            dao_graph.nodes[name]['weight'] = reduce_weigths(weights, current_timestep)
          projects[project_name] = team

    # actions in projects by day
    for project_name, team in projects.items():
      for name, weights in team.items():
        # do an action per team member (in 40% of the time) or nothing (in 60% of the time)
        new_weight = random.choice([do_discord_action(), do_github_action(), 0, 0, 0])
        if new_weight > 0:
          team[name].append((new_weight, current_timestep))
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