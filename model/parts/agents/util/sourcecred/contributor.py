from .oceanrounds import round11_stats, round12_stats, round13_stats, probabilities
from .contribution import Contribution, NFT, GithubEdgeWeight, GithubNodeWeight, DiscordEdgeWeight, DiscordNodeWeight, OceanNFT, ProofOf
from ...util.nft import Weight
import math
import networkx as nx
import random
import names
import functools
import operator
from typing import List


# +
# Here we mimic the size of the ecosystem per round 11-13. Each month a new round. We loop each round.
# Number of projects in each round here. We can change to random number of projects in a round. 
# Output is # of proposals and stakeholders for simulation. Generates a dictionary of projects with a name and a weight.
# Also generates total stakeholders and total votes. In total we get a project round simulation with real numbers, 
# comparable to current ecosystem

def generate_projects(round):
  round_stats = round11_stats
  if round % 3 == 0:
    round_stats = round12_stats
  if round % 3 == 1:
    round_stats = round13_stats
  project_number = round_stats['granted']
  mean = 0.5 # randomly set by Marc.
  sigma = round_stats['max_votes']/round_stats['total_votes'] # purely Marc inspiration. Can probably be regression modelled if one wants more detail
  size = math.floor(round_stats['total_votes']/1000)
  probs = probabilities(project_number, mean, sigma, size)
  projects = {}
  for prob in probs:
    projects['Project ' + names.get_last_name()] = prob
  return (projects, round_stats['total_stakeholders'], round_stats['total_votes'])

# +
# Assigns team members with roles and according to size of project we add more members - 
# small(<0.05 = 3 people)/medium/big(>0.1 = 5 members)
# members picked randomly from the 5 roles in the parameters in the model - engineers, architects, etc. Can we tailored

def generate_team_members(weight, roles, current_timestep):
  team_members = {}  
  if weight <= 0.05:
    role = random.choice(roles)
    team_members[role + ' ' + names.get_first_name()] = [Weight(weight/3, current_timestep)]
    roles.remove(role)
    role = random.choice(roles)
    team_members[role + ' ' + names.get_first_name()] = [Weight(weight/3, current_timestep)]
  if weight > 0.05 and weight <= 0.1:
    role = random.choice(roles)
    team_members[role + ' ' + names.get_first_name()] = [Weight(weight/4, current_timestep)]
    roles.remove(role)
    role = random.choice(roles)
    team_members[role + ' ' + names.get_first_name()] = [Weight(weight/4, current_timestep)]
    roles.remove(role)
    role = random.choice(roles)
    team_members[role + ' ' + names.get_first_name()] = [Weight(weight/4, current_timestep)]
  if weight > 0.1:
    role = random.choice(roles)
    team_members[role + ' ' + names.get_first_name()] = [Weight(weight/5, current_timestep)]
    roles.remove(role)
    role = random.choice(roles)
    team_members[role + ' ' + names.get_first_name()] = [Weight(weight/5, current_timestep)]
    roles.remove(role)
    role = random.choice(roles)
    team_members[role + ' ' + names.get_first_name()] = [Weight(weight/5, current_timestep)]
    roles.remove(role)
    role = random.choice(roles)
    team_members[role + ' ' + names.get_first_name()] = [Weight(weight/5, current_timestep)]
  return team_members

# +
# Ref article the distribution of activities should mimic a graph to visualize what happens round by round.
# Graph is easy to use to accumulate weights on edges and total value each stakeholder/member accumulates.
# Sourcecred is a complex markow chain, for simulation purposes we try to design simple.
# outcome is a project graph, mimicking sourcecred

def generate_project_graph(project_name, project_weight, roles, current_timestep):
  pl = 'Project Lead ' + names.get_first_name()
  graph = nx.DiGraph()
  graph.add_node(pl)
  graph.add_node(project_name, weight=project_weight)
  graph.add_edge(project_name, pl, weight=Contribution.PROPOSAL.value)
  team_members = generate_team_members(project_weight, roles, current_timestep)
  team_size = len(team_members.keys())
  team = {pl:[Weight(project_weight/(team_size + 1),current_timestep)] , **team_members}
  for name, weights in team_members.items():
    graph.add_node(name)
    graph.add_edge(project_name, name, weight=reduce_weigths(weights, current_timestep))
  return (team, graph)


def append_team_weights(team: dict, cred, current_timestep):
  for name in team.keys():
    team[name].append(Weight(cred, current_timestep))
  return team

# +
# Whales, Dolphin, Fish, Shrimp are adopted from Ocean pictures in Ocean Port, but generalised "size"

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

# +
# See Sankey plot from phase 1 of the research program. 
# In general you have 10 voters staking/voting for a project. Selection random here for simulation

def select_entities(amount, entities):
  e_list = list(entities.keys())
  entitys = e_list.copy()
  selection = {}
  for i in range(0,amount):
    if len(entitys) == 0:
      return selection
    entry = random.choice(entitys)
    selection[entry] = entities[entry]
    entitys.remove(entry)
  return selection

# +
# The voters that vote for a certain project with a certain weight (votes they use)
# Weight is currently linear, no quadratic voting or other fancy stuff

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
    project_stakers = math.floor(random.choice([0.1, 0.2, 0.3]) * stakeholder_size)
    print("Project Stakers: ", project_stakers)
    project_whales = select_entities(math.floor(0.2*project_stakers), whales)
    project_dolphins = select_entities(math.floor(0.2*project_stakers), dolphins)
    project_fish = select_entities(math.floor(0.3*project_stakers), fish)
    project_shrimps = select_entities(math.floor(0.3*project_stakers), shrimps)
    stakers = {**project_whales, **project_dolphins, **project_fish, **project_shrimps}
    for name, weight in stakers.items():
      graph.add_node(name)
      graph.add_edge(name, project_name, weight=weight)
  return graph

def reach_milestone(milestone_nr, weight):
  return (milestone_nr * weight)

def reach_roi(weight, factor):
  return (factor * weight)

def finish_project(weight, factor):
  return (factor * weight)

def check_last_milestone(milestones):
  # print("Milestones: ", milestones)
  for k, v in milestones.items():
    if k == 'Milestone1' and v == False: return 0
    if k == 'Milestone2' and v == False: return 1
    if k == 'Milestone3' and v == False: return 2
    if k == 'Milestone4' and v == False: return 3
    if k == 'Milestone4' and v == True: return 4
  return 0

def mint_nft(cred):
  if cred > 0 and cred < 10:
    return OceanNFT.SHRIMP
  if cred > 10 and cred < 20:
    return OceanNFT.OYSTER
  if cred > 20 and cred < 50:
    return OceanNFT.FISH
  if cred > 50 and cred < 100:
    return OceanNFT.DOLPHIN
  if cred > 100 and cred < 200:
    return OceanNFT.FISHERMAN
  if cred > 200 and cred < 500:
    return OceanNFT.MANTA
  if cred > 500 and cred < 1000:
    return OceanNFT.OCEAN
  if cred > 1000:
    return OceanNFT.ATLANTIS
  return OceanNFT.SHRIMP
  

# def decay_function(cred):
#   if cred < 10:
#     return 1
#   if cred > 10:
#     return (1-1/(0.1 * cred + 2))
#   if cred > 100:
#     return (1-1/(0.01 * cred + 5))
#   if cred > 1000:
#     return (1-1/(0.001 * cred + 5))
#   return 1

def pay_out(votes, project_weight, stakeholder_weight, constant):
  return (stakeholder_weight/project_weight) * votes * constant

# half_life = [0.5**i for i in range(50)]
# def decay(initial_timestep, current_timestep, decay_list = half_life):
#   time_passed = current_timestep - initial_timestep
#   if time_passed % 7 == 0:
#     return decay_list[math.floor(time_passed/7)]
#   else:
#     return 1

# def decayed_weight(weight:tuple, current_timestep):
#   return weight[0] * decay(weight[1], current_timestep)

def reduce_weigths(weights:List[Weight], current_timestep):
  decayed_weigths = []
  for i in range(len(weights)):
    weights[i].decay(current_timestep)
    new_weight = weights[i].total
    decayed_weigths.append(new_weight)
  return functools.reduce(operator.add, decayed_weigths)

def get_team_weight(team, current_timestep):
  total = 0
  for name, weights in team.items():
    cred = reduce_weigths(weights, current_timestep)
    if 'Project Lead' in name:
      total += cred * 2
    else:
      if 'Lead' in name:
        total += cred * 1.5
      else:
        total += cred
  return total

# def assess_project(team, funds_requested):
#   weight = get_team_weight(team)
#   return weight * funds_requested * 0.1

def do_discord_action():
  return random.choice(list(DiscordEdgeWeight))

def do_github_action():
  return random.choice(list(GithubEdgeWeight))

def do_contribution_action():
  return random.choice(list(Contribution))

def do_proof():
  return random.choice(list(ProofOf))
