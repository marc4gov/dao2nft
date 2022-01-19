import math
import random
import names

import networkx as nx
from model.parts.agents.util.sourcecred.contribution import (GithubEdgeWeight,
                                                       GithubNodeWeight, Contribution)
from model.parts.agents.util.sourcecred.contributor import make_contributor, add_contribution



def grants_policy(params, step, sH, s):
    """
    Update the grants state.
    """
    current_timestep = len(sH)
    timestep_per_day = 1
    timestep_per_month = 30

    # adjust the grant CAP according to the amount of valuable projects in this round
    if (current_timestep % timestep_per_month) == 0:
      value_ratio = (s['valuable_projects'] - s['unsound_projects']) / len(s['projects'])
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
    agents = s['agents']
    projects = s['projects']

    # new Grants round
    if (current_timestep % timestep_per_month) == 0:
        return ({
          'projects': [],
          'agents': [],
          'dao_graph': nx.DiGraph()
        })
    
    # initiate proposal by coinflip
    proposal = random.randint(0,2)
    if proposal == 1:
      contribution = "Proposal"
      agent = 'Project Manager ' + names.get_first_name()
      agents.append(agent)
      graph = nx.DiGraph()
      graph.add_node(agent)
      graph.add_node(contribution)
      graph.add_edge(agent, contribution, weight=Contribution.PROPOSAL)
      projects.append(graph)
      
      dao_graph.add_node(graph)

    # increase projects by day

    return ({
      'projects': projects,
      'agents' : agents,
      'dao_graph': dao_graph
    })


def values_policy(params, step, sH, s):
    """
    What kind of projects deliver good value?
    """
    current_timestep = len(sH)
    timestep_per_day = 1
    timestep_per_month = 30

    # new Grants round
    if (current_timestep % timestep_per_month) == 0:
      return ({
          'valuable_projects': 0,
          'unsound_projects': 0,
          'yes_votes': math.floor(0.8 * s['voters']),
          'no_votes': math.floor(0.2 * s['voters']),
      })

    # every day we assess the projects to either valuable or unsound and adjust the project properties and vote signal accordingly
    projects = len(s['projects'])
    valuable = math.floor(random.choice(params['dataset_ratio']) * projects)
    valuable_increment = 1
    if valuable <= s['valuable_projects'] and s['valuable_projects'] > 0:
      valuable_increment = -1
    unsound_increment = 1
    unsound = math.floor(random.choice(params['unsound_ratio']) * len(s['projects']))
    if unsound <= s['unsound_projects'] and s['unsound_projects'] > 0:
      unsound_increment = -1  
    projects = projects if projects > 0 else 1
    yes_votes = s['yes_votes'] if s['yes_votes'] > 0 else 1 # divison by zero hack
    no_votes = s['no_votes'] if s['no_votes'] > 0 else 1
    value_ratio = (valuable - unsound) / projects
    
    return ({
        'valuable_projects': s['valuable_projects'] + valuable_increment,
        'unsound_projects': s['unsound_projects'] + unsound_increment,
        'yes_votes': math.floor(s['yes_votes'] * (1 + value_ratio)),
        'no_votes': math.floor(s['no_votes'] * (1 - value_ratio)),
    })

def participation_policy(params, step, sH, s):
    """
    Update the projects state.
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
