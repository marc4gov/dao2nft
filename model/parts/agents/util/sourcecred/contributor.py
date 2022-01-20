from .oceanrounds import round11_stats, round12_stats, round13_stats, probabilities
from .contribution import Contribution
import math
import networkx as nx
import random
import names

def make_contributor(name, contributions):
  contributor = {
    'name': name,
    'contributions': contributions
  }
  return contributor

def add_contribution(contributor, contribution):
  contributor.append(contribution)
  return contributor

def generate_projects(round):
  round_stats = round11_stats
  if round % 3 == 0:
    round_stats = round12_stats
  if round % 3 == 1:
    round_stats = round13_stats
  project_number = round_stats['granted']
  mean = 0.5
  sigma = round_stats['max_votes']/round_stats['total_votes']
  size = math.floor(round_stats['total_votes']/1000)
  probs = probabilities(project_number, mean, sigma, size)
  projects = {}
  for prob in probs:
    projects['Project ' + names.get_last_name()] = prob
  return (projects, round_stats['total_stakeholders'], round_stats['total_votes'])

def generate_team_members(weight, roles):
  team_members = {}  
  if weight <= 0.05:
    role = random.choice(roles)
    team_members[role + ' ' + names.get_first_name()] = weight/3
    roles.remove(role)
    role = random.choice(roles)
    team_members[role + ' ' + names.get_first_name()] = weight/3
  if weight > 0.05 and weight <= 0.1:
    role = random.choice(roles)
    team_members[role + ' ' + names.get_first_name()] = weight/4
    roles.remove(role)
    role = random.choice(roles)
    team_members[role + ' ' + names.get_first_name()] = weight/4
    roles.remove(role)
    role = random.choice(roles)
    team_members[role + ' ' + names.get_first_name()] = weight/4
  if weight > 0.1:
    role = random.choice(roles)
    team_members[role + ' ' + names.get_first_name()] = weight/5
    roles.remove(role)
    role = random.choice(roles)
    team_members[role + ' ' + names.get_first_name()] = weight/5
    roles.remove(role)
    role = random.choice(roles)
    team_members[role + ' ' + names.get_first_name()] = weight/5
    roles.remove(role)
    role = random.choice(roles)
    team_members[role + ' ' + names.get_first_name()] = weight/5
  return team_members


def generate_project_graph(project_name, project_weight, roles):
  pl = 'Project Lead ' + names.get_first_name()
  graph = nx.DiGraph()
  graph.add_node(pl)
  graph.add_node(project_name, weight=project_weight)
  graph.add_edge(project_name, pl, weight=Contribution.PROPOSAL.value)
  team_members = generate_team_members(project_weight, roles)
  team_size = len(team_members.keys())
  team = {pl:project_weight/(team_size + 1), **team_members}
  for name, weight in team_members.items():
    graph.add_node(name)
    graph.add_edge(pl, name, weight=weight)
  return (team, graph)

def generate_stakeholders(weights):
  stakeholders = {}
  for weight in weights:
    if weight > 0.1:
        stakeholders['Whale ' + names.get_first_name()] = weight
    if weight > 0.05 and weight <= 0.1:
        stakeholders['Dolphin ' + names.get_first_name()] = weight
    if weight > 0.01 and weight <= 0.05:
        stakeholders['Fish ' + names.get_first_name()] = weight
    if weight <= 0.01:
        stakeholders['Shrimp ' + names.get_first_name()] = weight
  return stakeholders

def select_stakers(amount, stakers):
  staker_list = list(stakers.keys())
  print(staker_list)
  stakers2 = staker_list.copy()
  selection = {}
  for i in range(0,amount):
    if len(stakers2) == 0:
      return selection
    entry = random.choice(stakers2)
    selection[entry] = stakers[entry]
    stakers2.remove(entry)
  return selection

def generate_stakeholder_graph(projects, stakeholder_size, total_votes):
  graph = nx.DiGraph()
  weights = probabilities(stakeholder_size, 1.0, random.choice([0.3, 0.4, 0.5, 0.6]), total_votes)
  
  stakeholders = generate_stakeholders(weights)
  whales  = {k:v for k,v in stakeholders.items() if 'Whale' in k}
  dolphins = {k:v for k,v in stakeholders.items() if 'Dolphin' in k}
  fish = {k:v for k,v in stakeholders.items() if 'Fish' in k}
  shrimps = {k:v for k,v in stakeholders.items() if 'Shrimp' in k}
  for project_name, project_weight in projects.items():
    print(project_name)
    project_stakers = math.floor(random.choice([0.4, 0.5, 0.6]) * stakeholder_size)
    print("Project Stakers: ", project_stakers)
    project_whales = select_stakers(math.floor(0.2*project_stakers), whales)
    project_dolphins = select_stakers(math.floor(0.2*project_stakers), dolphins)
    project_fish = select_stakers(math.floor(0.3*project_stakers), fish)
    project_shrimps = select_stakers(math.floor(0.3*project_stakers), shrimps)
    stakers = {**project_whales, **project_dolphins, **project_fish, **project_shrimps}
    for name, weight in stakers.items():
      graph.add_node(name)
      graph.add_edge(name, project_name, weight=weight)
  return graph