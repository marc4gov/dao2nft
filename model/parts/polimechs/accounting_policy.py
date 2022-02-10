from model.parts.agents.util.sourcecred.contributor import get_total_votes, accounting, curateProject, check_milestones
from model.parts.agents.Curator import Curator, Verdict
import math

def accounting_policy(params, step, sH, s):
    """
    Update the voters state.
    """
    current_timestep = len(sH)
    timestep_per_day = 1
    timestep_per_month = 30

    voters = s['voters']
    total_votes = get_total_votes(voters)

    projects = s['projects']

    # per new Grants round
    if (current_timestep % timestep_per_month) == 0:

      # bring out the Curator!
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
      print(curator)
      #do accounting
      voters = accounting(curator, voters)
      total_votes_accounted = get_total_votes(voters)
      ratio = total_votes_accounted/total_votes
      if total_votes_accounted >= total_votes:
        pass

    return ({
      'voters': voters,
    })