from model.parts.agents.util.sourcecred.contributor import get_total_votes, check_milestones
from model.parts.agents.Curator import Curator, Verdict
from model.parts.agents.Project import Project
from model.parts.agents.Voter import Voter
from typing import List


import math

# here the curation is updated based on curators' verdict similar quantifying praise in TEC. 
# Tuple list with project name and verdict and then matched to projects that were voted upon via python list comprehension
# if verdict is losing the effect is here - a rugpull is then 5x being late per curate function and accounting policy in polimech
# here we could potentially add an exponential slashing/reward policy to adjust exponentially, need to understand how 
# such a function  affects voting in next round if we choose to do this

# if need to curate here is the curate function

def curateProject(project:Project, current_timestep):
  milestones = project.milestones
  delayed = 0
  delivered = 0
  in_progress = 0
  finished = False
  for m in milestones:
    if m.actual > current_timestep:
      delayed += current_timestep - m.actual
    elif m.actual <= current_timestep and m.actual > 0:
      delivered += 1
    else:
      in_progress += 1
  if delivered == len(milestones):
    finished = True
  return (delayed, delivered, in_progress, finished)

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
        # print("Voter wins: ", voter.name, tokens * 0.1)
        voter.winTokens(tokens * 0.1)
      else:
        # print("Voter loses: ", voter.name, tokens * status.value * 0.05)
        voter.slashTokens(tokens * status.value * 0.05)
    accounted_voters.append(voter)
  return accounted_voters

def accounting_policy(params, step, sH, s):
    """
    Update the voters state.
    """
    current_timestep = len(sH)
    timestep_per_day = 1
    timestep_per_month = 30

    voters = s['voters']
    total_votes = get_total_votes(voters)
    dao_members = s['dao_members']
    projects = s['projects']

    # per new Grants round
    if (current_timestep % timestep_per_month) == 0:

      # bring out the Curator! Every month curator reviews projects whether milestones are met. 
    # Tracking from curate update function. Adversary is someone going againts value of ecosystem, "rugpull" 
    # is someone just taking tokens and running away and never hear from them
    
      curator = Curator('Curator OCEANDao', 1, 0)
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
          if delayed > 21:
            curator.addAudit(project.name, Verdict.RUGPULL)
        else:
          curator.addAudit(project.name, Verdict.DELIVERED)
      # print(curator)
      #do accounting
      voters = accounting(curator, voters)
      total_votes_accounted = get_total_votes(voters)
      ratio = total_votes_accounted/total_votes
      dao_members *= (1 + ratio)

    return ({
      'voters': voters,
      'dao_members' : dao_members
    })
