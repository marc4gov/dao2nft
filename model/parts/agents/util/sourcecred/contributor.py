from model.parts.agents.Curator import Curator, Verdict
from .oceanrounds import round11_stats, round12_stats, round13_stats, probabilities
from .contribution import Contribution, TaskType, GithubEdgeWeight, GithubNodeWeight, DiscordEdgeWeight, DiscordNodeWeight, OceanNFT, ProofOf
from ...util.nft import Weight, OceanNFT
from ...util.wallet import Wallet
from ....agents.GrantRound import GrantRound
from ....agents.Voter import Voter
from ....agents.Project import Project, TeamMember, Milestone, Task, TeamMemberType

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

def generate_project_weights(round):
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
# members picked from the 5 roles in the parameters in the model - engineers, architects, etc. Can be tailored


def generate_team_members(weight, current_timestep):
  team_members = [] 
  if weight <= 0.05:
    team_members.append(TeamMember(names.get_first_name(), TeamMemberType.ENGINEER, weight/3, current_timestep))
    team_members.append(TeamMember(names.get_first_name(), TeamMemberType.COMMUNITY_LEAD, weight/3, current_timestep))
  if weight > 0.05 and weight <= 0.1:
    team_members.append(TeamMember(names.get_first_name(), TeamMemberType.ENGINEER, weight/4, current_timestep))
    team_members.append(TeamMember(names.get_first_name(), TeamMemberType.DESIGNER, weight/4, current_timestep))
    team_members.append(TeamMember(names.get_first_name(), TeamMemberType.COMMUNITY_LEAD, weight/4, current_timestep))
  if weight > 0.1:
    team_members.append(TeamMember(names.get_first_name(), TeamMemberType.ENGINEER, weight/5, current_timestep))
    team_members.append(TeamMember(names.get_first_name(), TeamMemberType.DESIGNER, weight/5, current_timestep))
    team_members.append(TeamMember(names.get_first_name(), TeamMemberType.COMMUNITY_LEAD, weight/5, current_timestep))
    team_members.append(TeamMember(names.get_first_name(), TeamMemberType.LEAD_ENGINEER, weight/5, current_timestep))
  return team_members

# +
# Ref article the distribution of activities should mimic a graph to visualize what happens round by round.
# Graph is easy to use to accumulate weights on edges and total value each stakeholder/member accumulates.
# Sourcecred is a complex markow chain, for simulation purposes we try to design simple.
# outcome is a project graph, mimicking sourcecred

def generate_project(project_name, project_weight, current_timestep, grant):
  wallet = Wallet(0,grant)
  project = Project(project_name, project_weight, current_timestep, wallet)
  team_members = generate_team_members(project_weight, current_timestep)
  team_size = len(team_members)
  project.addMember(TeamMember(names.get_first_name(), TeamMemberType.PROJECT_LEAD, project_weight/(team_size + 1), current_timestep))
  for member in team_members:
    project.addMember(member)
  project.generateMilestones(current_timestep)
  return project

def append_team_weights(team: dict, cred, current_timestep):
  for name in team.keys():
    team[name].append(Weight(cred, current_timestep))
  return team

def curateProject(project:Project, current_timestep):
  milestones = project.milestones
  delayed = 0
  delivered = 0
  in_progress = 0
  finished = False
  for m in milestones:
    if m.planned < current_timestep:
      delayed += current_timestep - m.planned
    elif m.actual <= current_timestep and m.actual > 0:
      delivered += 1
    else:
      in_progress += 1
  if delivered == len(milestones):
    finished = True
  return (delayed, delivered, in_progress, finished)

def generate_voters(round, current_timestep, project_weights):
  voters = []
  round_stats = round11_stats
  if round % 3 == 0:
    round_stats = round12_stats
  if round % 3 == 1:
    round_stats = round13_stats
  voter_number = round_stats['total_stakeholders']
  mean = 0.5 # randomly set by Marc.
  sigma = round_stats['max_votes']/round_stats['total_votes'] # purely Marc inspiration. Can probably be regression modelled if one wants more detail
  size = math.floor(round_stats['total_votes']/1000)
  probs = probabilities(voter_number, mean, sigma, size)
  for weight in probs:
    votes = weight * round_stats['total_votes']
    sorted_project_weights = dict(sorted(project_weights.items(), key=lambda item: item[1]))
    voter = Voter('Voter ' + names.get_first_name(), weight, current_timestep, Wallet(0, votes))
    for name, project_weight in sorted_project_weights.items():
      voter.addVote(name, project_weight * votes)
    voters.append(voter)
  return voters



def accounting(curator:Curator, voters:List[Voter]) -> List[Voter]:
  accounted_voters = []
  dverdicts = dict(curator.audits)
  for voter in voters:
    dvotes = dict(voter.votes)
    matches = [(dverdicts[k], dvotes[k])  for k in dverdicts.keys()&dvotes.keys()]
    for match in matches:
      status = match[0]
      tokens = match[1]
      if status == Verdict.DELIVERED:
        print("Voter wins: ", voter.name, tokens * 0.1)
        voter.winTokens(tokens * 0.1)
      else:
        # print("Voter loses: ", voter.name, tokens * status.value * 0.01)
        voter.slashTokens(tokens * status.value * 0.01)
    accounted_voters.append(voter)
  return accounted_voters

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
  

def pay_out(votes, project_weight, stakeholder_weight, constant):
  return (stakeholder_weight/project_weight) * votes * constant

def reduce_weigths(weights:List[Weight], current_timestep):
  decayed_weigths = []
  for i in range(len(weights)):
    weights[i].decay(current_timestep)
    new_weight = weights[i].total
    decayed_weigths.append(new_weight)
  return functools.reduce(operator.add, decayed_weigths)

def get_team_weight(members:List[TeamMember], current_timestep):
  total = 0
  for member in members:
    member.reduceWeights(current_timestep)
    cred = member.current_weight
    if 'Project Lead' in member.name:
      total += cred * 2
    else:
      if 'Lead' in member.name:
        total += cred * 1.5
      else:
        total += cred
  return total

def get_total_votes(voters:List[Voter]):
  tokens = 0
  for i in range(len(voters)):
    tokens += voters[i].wallet.OCEAN()
  return tokens

def do_discord_action():
  return random.choice(list(DiscordEdgeWeight))

def do_github_action():
  return random.choice(list(GithubEdgeWeight))

def do_contribution_action():
  return random.choice(list(Contribution))

def do_proof():
  return random.choice(list(ProofOf))
