import random
import math

def grants_policy(params, step, sH, s):
    """
    Update the grants state.
    """
    current_timestep = len(sH)
    timestep_per_day = 1
    timestep_per_month = 30

    if (current_timestep % timestep_per_month) == 0:
      return ({'grant_cap': math.floor((1 + random.randint(3,5) * s['projects']/s['grant_cap']) * s['grant_cap'])})

    return ({'grant_cap': s['grant_cap'] })

def projects_policy(params, step, sH, s):
    """
    Update the projects state.
    """
    current_timestep = len(sH)
    timestep_per_day = 1
    timestep_per_month = 30

    # new Grants round
    if (current_timestep % timestep_per_month) == 0:
        return ({'projects': 0})
    
    # increase projects by day
    return ({'projects': random.randint(0,1) + s['projects']})


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
    
    valuable = math.floor(random.choice(params['dataset_ratio']) * s['projects'])
    valuable_increment = 1
    if valuable <= s['valuable_projects'] and s['valuable_projects'] > 0:
      valuable_increment = -1
    unsound_increment = 1
    unsound = math.floor(random.choice(params['unsound_ratio']) * s['projects'])
    if unsound <= s['unsound_projects'] and s['unsound_projects'] > 0:
      unsound_increment = -1  
    projects = s['projects'] if s['projects'] > 0 else 1
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

    unsound_projects = s['unsound_projects'] if s['unsound_projects'] > 0 else 1
    valuable_projects = s['valuable_projects'] if s['valuable_projects'] > 0 else 1
    projects = s['projects'] if s['projects'] > 0 else 1
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